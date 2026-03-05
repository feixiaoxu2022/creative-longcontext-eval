#!/usr/bin/env python3
"""
将 singleturn_dataset.jsonl 导出为人类可读的目录结构。

每条数据导出为一个目录，包含：
  - meta.json   — 元数据（不含大文本）
  - input.md    — 组装好的输入文本
  - reference_output.txt — 参考输出
  - judge_criteria.md — 评判标准

用法：
    python3 export_readable.py singleturn_dataset.jsonl readable/
"""

import json
import os
import sys


def export_readable(jsonl_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    items = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            items.append(json.loads(line))

    # 写 index.md
    index_lines = [f"# 单轮长上下文评测数据集 ({len(items)} 条)\n"]
    index_lines.append("| # | ID | 场景 | 产出物 | 题材 | 模型 | input_tokens | length_bin |")
    index_lines.append("|---|----|----|--------|------|------|-------------|-----------|")

    for i, item in enumerate(items):
        idx = f"{i+1:03d}"
        dir_name = f"{idx}_{item['scenario']}_{item['stage']}"
        item_dir = os.path.join(output_dir, dir_name)
        os.makedirs(item_dir, exist_ok=True)

        # meta.json — 元数据
        meta = {k: v for k, v in item.items()
                if k not in ("input", "reference_output", "judge_criteria", "system_prompt")}
        with open(os.path.join(item_dir, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        # input.md
        with open(os.path.join(item_dir, "input.md"), "w", encoding="utf-8") as f:
            f.write(item.get("input", ""))

        # reference_output.txt (仅在存在时生成)
        ref = item.get("reference_output", "")
        if ref:
            ext = ".json" if ref.lstrip().startswith("{") or ref.lstrip().startswith("[") else ".md"
            with open(os.path.join(item_dir, f"reference_output{ext}"), "w", encoding="utf-8") as f:
                f.write(ref)

        # judge_criteria.md
        criteria = item.get("judge_criteria", [])
        if criteria:
            with open(os.path.join(item_dir, "judge_criteria.md"), "w", encoding="utf-8") as f:
                f.write(f"# Judge Criteria ({len(criteria)} 条)\n\n")
                for jc in criteria:
                    name = jc.get('name') or jc.get('check_name', 'Unknown')
                    tier = jc.get('tier', 'N/A')
                    f.write(f"## {name} [{tier}]\n\n")
                    if 'criteria_text' in jc:
                        f.write(jc['criteria_text'].strip())
                        f.write("\n\n---\n\n")
                    else:
                        f.write("(评判标准未记录)\n\n---\n\n")

        # index 行
        index_lines.append(
            f"| {idx} | [{dir_name}](./{dir_name}/) | {item['scenario']} | "
            f"{item.get('output_type', '')} | {item.get('genre', '')} | "
            f"{item['source_model'][:20]} | {item['input_tokens_est']:,} | {item['length_bin']} |"
        )

    # 写 index
    with open(os.path.join(output_dir, "index.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(index_lines) + "\n")

    print(f"导出 {len(items)} 条到 {output_dir}/")
    print(f"索引: {output_dir}/index.md")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python3 export_readable.py <jsonl_path> <output_dir>")
        sys.exit(1)
    export_readable(sys.argv[1], sys.argv[2])
