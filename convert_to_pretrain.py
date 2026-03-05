#!/usr/bin/env python3
"""
将 instruct 模式的 singleturn 数据集改造为 pretrain completion 模式。

核心改造:
1. 去掉所有指令类内容(系统设定、用户需求、参考文档、当前任务)
2. 去掉结构化前置设定(角色卡、大纲、配方、选题简报等 JSON 设定文档)
3. 只保留已完成的正文/剧本内容作为 prefix
4. NTS/SD 的 JSON schema 剧本转为自然语言格式
5. 删除 reference_output 和 reference_output_tokens_est (pretrain 模式用不到)
6. 丢弃无法续写的数据(无正文可做 prefix 的)

用法:
    python3 convert_to_pretrain.py --input singleturn_dataset.jsonl --output pretrain_dataset.jsonl
"""

import argparse
import json
import re
import sys
from pathlib import Path


# ============================================================
# 跳过规则
# ============================================================

def should_skip(item):
    """判断是否应该跳过(无正文可做 prefix)。返回 (skip: bool, reason: str)"""
    scenario = item["scenario"]
    stage = item["stage"]

    # NTS/analysis: 无 prior files, 不是续写任务
    if scenario == "nts" and stage == "analysis":
        return True, "nts/analysis: 无 prior files"

    # SD/outline: prior_files 只有 JSON 设定(topic_brief + characters)
    if scenario == "sd" and stage == "outline":
        return True, "sd/outline: prior_files 只有 JSON 设定"

    # NTS/script_writing 第1集: prior_files 只有 JSON 设定(novel_analysis + drama_plan)
    if scenario == "nts" and stage == "script_writing":
        text = item["input"]
        start = text.find("# 已有创作成果")
        end = text.find("# 当前任务")
        if start >= 0:
            prior_section = text[start:end] if end > start else text[start:]
            if "scripts/" not in prior_section and "chapters/" not in prior_section:
                return True, "nts/script_writing: 无 prior scripts(第1集)"

    return False, ""


# ============================================================
# NTS JSON 剧本 → 自然语言
# ============================================================

def convert_nts_episode(data):
    """NTS 剧本 JSON → 自然语言，兼容多种 key 变体"""
    lines = []

    # episode_number/title: 兼容 episode_info 嵌套结构
    ep_info = data.get("episode_info", {})
    ep = data.get("episode_number", "") or ep_info.get("episode_number", "")
    title = data.get("title", "") or ep_info.get("episode_title", "")
    if ep or title:
        lines.append(f"第{ep}集 {title}")
        lines.append("")

    scenes = data.get("scenes", []) or data.get("scene_list", []) or data.get("场景列表", [])
    for i, sc in enumerate(scenes):
        sn = sc.get("scene_number", i + 1)
        lines.append(f"场景{sn}")

        loc = sc.get("location", "")
        time_ = sc.get("time_of_day", "") or sc.get("time", "")
        atm = sc.get("atmosphere", "")
        if loc:
            lines.append(f"地点：{loc}")
        if time_:
            lines.append(f"时间：{time_}")
        if atm:
            lines.append(f"氛围：{atm}")
        shot = sc.get("initial_shot", "") or sc.get("opening_shot", "")
        if shot:
            lines.append(shot)
        lines.append("")

        # content 列表: 兼容 "content", "sequence", "content_sequence" key
        content = sc.get("content", []) or sc.get("sequence", []) or sc.get("content_sequence", [])
        for c in content:
            type_ = c.get("type", "")
            # text 字段: 兼容 "text", "content", "description", "line"
            text = c.get("text", "") or c.get("content", "") or c.get("description", "")
            char = c.get("character", "")
            emotion = c.get("emotion", "")

            if type_ == "dialogue":
                dial_text = c.get("line", "") or text
                if emotion:
                    lines.append(f"{char}（{emotion}）：{dial_text}")
                else:
                    lines.append(f"{char}：{dial_text}")
            elif type_ == "inner_voice":
                if char:
                    lines.append(f"（{char}内心）{text}")
                else:
                    lines.append(f"（内心）{text}")
            elif type_ == "sound":
                lines.append(f"（{text}）")
            elif type_ == "effect":
                lines.append(f"（{text}）")
            else:  # action
                lines.append(text)
        lines.append("")

    return "\n".join(lines).strip()


# ============================================================
# SD JSON 剧本 → 自然语言
# ============================================================

def convert_sd_episode(data):
    """SD 剧本 JSON → 自然语言"""
    lines = []
    ep = data.get("episode_number", "")
    title = data.get("title", "")
    if ep or title:
        lines.append(f"第{ep}集 {title}")
        lines.append("")

    scenes = data.get("scenes_detail", []) or data.get("scenes", [])
    for i, sc in enumerate(scenes):
        sn = sc.get("scene_number", i + 1)
        lines.append(f"场景{sn}")

        h = sc.get("scene_header", {})
        if isinstance(h, dict):
            loc = h.get("location", "")
            time_ = h.get("time", "")
            atm = h.get("atmosphere", "")
        else:
            loc, time_, atm = "", "", ""

        if loc:
            lines.append(f"地点：{loc}")
        if time_:
            lines.append(f"时间：{time_}")
        if atm:
            lines.append(f"氛围：{atm}")
        lines.append("")

        for c in sc.get("content", []):
            if isinstance(c, str):
                # 有些 SD 剧本的 content 直接是字符串
                lines.append(c)
                continue
            type_ = c.get("type", "")
            if type_ == "dialogue":
                char = c.get("character", "")
                line_ = c.get("line", "") or c.get("text", "")
                lines.append(f"{char}：{line_}")
            elif type_ == "emotion":
                desc = c.get("description", "") or c.get("text", "")
                lines.append(f"（{desc}）")
            else:  # action
                desc = c.get("description", "") or c.get("text", "")
                lines.append(desc)
        lines.append("")

    return "\n".join(lines).strip()


# ============================================================
# JSON 剧本转换入口
# ============================================================

def convert_episode_to_text(json_str, scenario):
    """JSON 剧本 → 自然语言"""
    data = json.loads(json_str)
    if scenario == "nts":
        return convert_nts_episode(data)
    elif scenario == "sd":
        return convert_sd_episode(data)
    else:
        return json_str  # fallback


# ============================================================
# 从 input 中提取已完成正文/剧本
# ============================================================

# 要跳过的 JSON 设定文件模式
SKIP_PATTERNS = [
    "creative_intent",
    "characters.json",
    "outline.json",
    "outline_",
    "topic_brief",
    "novel_analysis",
    "drama_plan",
]


def parse_file_blocks(section):
    """解析 ### filename 块，返回 [(filename, content), ...]

    只匹配形如 ### xxx.json 或 ### chapters/xxx.md 的行（即带文件扩展名的），
    而不是所有 ### 开头的行（章节正文内部可能也有 ### 标题）。
    """
    blocks = []
    # 只匹配带文件扩展名的 ### 行
    pattern = re.compile(r"^### (\S+\.\w+)\s*$", re.MULTILINE)
    matches = list(pattern.finditer(section))

    for idx, m in enumerate(matches):
        filename = m.group(1)
        block_start = m.end()
        if idx + 1 < len(matches):
            block_end = matches[idx + 1].start()
        else:
            block_end = len(section)
        content = section[block_start:block_end]
        # 对于 ## 子标题（如 "## 选题简报"、"## 角色卡" 等），
        # 只在非 .md/.json 文件时截断（.md 正文可能包含 ## 标题，JSON 可能包含 ## 字符串）
        if not filename.endswith(".md") and not filename.endswith(".json"):
            h2_match = re.search(r"\n## ", content)
            if h2_match:
                content = content[:h2_match.start()]
        blocks.append((filename, content.strip()))

    return blocks


def extract_novel_text(input_text):
    """从 NTS input 中提取原著小说文本（在 # 原著小说 和 # 已有创作成果 之间）"""
    novel_start = input_text.find("# 原著小说")
    if novel_start < 0:
        return ""
    prior_start = input_text.find("# 已有创作成果")
    if prior_start > novel_start:
        return input_text[novel_start:prior_start].strip()
    return input_text[novel_start:].strip()


def extract_completed_content(input_text, scenario):
    """从 instruct 版 input 中提取已完成正文/剧本部分"""

    result_parts = []

    # 0. NTS 场景：先提取原著小说（改编需要原著作为上下文）
    if scenario == "nts":
        novel_text = extract_novel_text(input_text)
        if novel_text:
            result_parts.append(novel_text)

    # 1. 定位 "已有创作成果" section
    prior_start = input_text.find("# 已有创作成果")
    task_start = input_text.find("# 当前任务")
    if prior_start < 0:
        return "\n\n".join(result_parts) if result_parts else ""
    section = input_text[prior_start:task_start] if task_start > 0 else input_text[prior_start:]

    # 2. 解析 ### filename 块
    blocks = parse_file_blocks(section)

    # 3. 过滤：只保留正文文件
    for filename, content in blocks:
        if not content:
            continue
        if any(pat in filename.lower() for pat in SKIP_PATTERNS):
            continue  # 跳过 JSON 前置设定

        if filename.endswith(".md"):
            # NWA 章节：纯文本直接保留
            result_parts.append(content)
        elif filename.endswith(".json") and ("scripts/" in filename or "script" in filename.lower()):
            # NTS/SD 剧本：JSON → 自然语言
            try:
                converted = convert_episode_to_text(content, scenario)
                result_parts.append(converted)
            except (json.JSONDecodeError, Exception) as e:
                # JSON 不合法，跳过该文件（不保留原始 JSON）
                print(f"警告: {filename} JSON 解析失败，跳过: {e}", file=sys.stderr)
                continue

    return "\n\n".join(result_parts)


# ============================================================
# 长度分箱
# ============================================================

def calculate_length_bin(tokens_est):
    """根据 token 估算值计算 length_bin"""
    if tokens_est < 10000:
        return "<10K"
    elif tokens_est < 20000:
        return "10K-20K"
    elif tokens_est < 40000:
        return "20K-40K"
    elif tokens_est < 70000:
        return "40K-70K"
    elif tokens_est < 100000:
        return "70K-100K"
    else:
        return "100K+"


# ============================================================
# 主流程
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="将 instruct 数据集转换为 pretrain completion 模式")
    parser.add_argument("--input", required=True, help="输入 JSONL 文件路径")
    parser.add_argument("--output", required=True, help="输出 JSONL 文件路径")
    parser.add_argument("--stats", action="store_true", help="输出统计信息")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"错误: 输入文件不存在: {input_path}", file=sys.stderr)
        sys.exit(1)

    # 读取
    items = []
    with open(input_path) as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))

    print(f"读入 {len(items)} 条数据")

    # 处理
    output_items = []
    skipped = []
    empty_content = []

    for item in items:
        skip, reason = should_skip(item)
        if skip:
            skipped.append((item["id"], reason))
            continue

        # 提取已完成正文
        text_content = extract_completed_content(item["input"], item["scenario"])

        if not text_content.strip():
            empty_content.append(item["id"])
            continue

        # 更新字段
        item["input"] = text_content
        item["input_tokens_est"] = len(text_content) // 3
        item["length_bin"] = calculate_length_bin(item["input_tokens_est"])

        # 同步 judge_criteria_count 元数据
        if "judge_criteria" in item:
            item["judge_criteria_count"] = len(item["judge_criteria"])

        # 删除 pretrain 模式下不需要的字段
        item.pop("reference_output", None)
        item.pop("reference_output_tokens_est", None)

        output_items.append(item)

    # 写出
    with open(output_path, "w") as f:
        for item in output_items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"\n输出 {len(output_items)} 条数据 → {output_path}")
    print(f"跳过 {len(skipped)} 条:")
    for item_id, reason in skipped:
        print(f"  - {item_id[:80]}: {reason}")
    if empty_content:
        print(f"\n警告: {len(empty_content)} 条提取后内容为空:")
        for item_id in empty_content:
            print(f"  - {item_id[:80]}")

    # 统计
    if args.stats or True:  # 默认输出统计
        print(f"\n=== 统计 ===")
        bins = {}
        scenarios = {}
        for item in output_items:
            b = item["length_bin"]
            bins[b] = bins.get(b, 0) + 1
            s = item["scenario"]
            scenarios[s] = scenarios.get(s, 0) + 1

        print(f"\n按场景:")
        for s, c in sorted(scenarios.items()):
            print(f"  {s}: {c}")

        print(f"\n按长度分箱:")
        bin_order = ["<10K", "10K-20K", "20K-40K", "40K-70K", "70K-100K", "100K+"]
        for b in bin_order:
            if b in bins:
                print(f"  {b}: {bins[b]}")

        # token 估算统计
        tokens = [item["input_tokens_est"] for item in output_items]
        if tokens:
            print(f"\ninput_tokens_est 分布:")
            print(f"  min: {min(tokens)}")
            print(f"  max: {max(tokens)}")
            print(f"  mean: {sum(tokens) // len(tokens)}")
            print(f"  median: {sorted(tokens)[len(tokens) // 2]}")

    # 自动生成统计报告和 readable 导出
    print(f"\n生成配套文件...")

    # 1. 生成统计报告
    generate_stats_report(output_items, output_path, len(items))

    # 2. 生成 readable 导出（暂时禁用，有 bug）
    # generate_readable_export(output_path)


def generate_stats_report(items, output_path, instruct_count):
    """生成 pretrain 数据集统计报告"""
    from collections import Counter

    tokens = [item["input_tokens_est"] for item in items]
    scenario_dist = Counter(item["scenario"] for item in items)
    length_dist = Counter(item["length_bin"] for item in items)
    stage_dist = Counter(item["stage"] for item in items)

    report = f"""# Pretrain 数据集统计 ({len(items)}条)

生成时间: {Path(output_path).stat().st_mtime}

## 基本信息

- **总计**: {len(items)} 条
- **来源**: 从 instruct 版 singleturn 数据集转换而来（{instruct_count}条 → {len(items)}条可续写）
- **转换方式**: 去除所有指令和 JSON 设定，只保留已完成正文/剧本（自然语言）
- **格式**: 无 reference_output，judge_criteria 格式已修复（无 YAML 头，标题从 ### 开始）

## 场景分布

"""

    for scenario, count in sorted(scenario_dist.items()):
        pct = count / len(items) * 100
        report += f"- **{scenario}**: {count} 条 ({pct:.1f}%)\n"

    report += "\n## 产出物类型分布\n\n"
    for stage, count in sorted(stage_dist.items()):
        pct = count / len(items) * 100
        report += f"- **{stage}**: {count} 条 ({pct:.1f}%)\n"

    report += "\n## 长度分布\n\n"
    for bin_name in ["<10K", "10K-20K", "20K-40K", "40K-70K", "70K-100K"]:
        count = length_dist.get(bin_name, 0)
        if count > 0:
            pct = count / len(items) * 100
            report += f"- **{bin_name}**: {count} 条 ({pct:.1f}%)\n"

    report += f"""
## Token 统计

- **平均**: {sum(tokens)/len(tokens):,.0f} tokens
- **中位数**: {sorted(tokens)[len(tokens)//2]:,} tokens
- **最小**: {min(tokens):,} tokens
- **最大**: {max(tokens):,} tokens

## 与 Instruct 版本的对比

- Instruct: {instruct_count} 条（完整指令格式，包含系统设定、用户需求、参考文档、当前任务）
- Pretrain: {len(items)} 条（纯正文/剧本，{instruct_count - len(items)}条因无prior内容或转换后为空被过滤）
- 转换损失: {(instruct_count - len(items))/instruct_count*100:.1f}%
"""

    stats_path = str(output_path).replace(".jsonl", "_stats.md")
    with open(stats_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"  ✓ 统计报告: {stats_path}")


def generate_readable_export(jsonl_path):
    """生成 readable 目录导出"""
    import subprocess
    import shutil

    # 调用 export_readable.py
    jsonl_path_str = str(jsonl_path)
    readable_dir = jsonl_path_str.replace(".jsonl", "").replace("pretrain_dataset", "readable")

    # 确保目录不存在（先删除）
    if os.path.exists(readable_dir):
        shutil.rmtree(readable_dir)

    # 调用 export_readable.py
    script_dir = Path(__file__).parent
    export_script = script_dir / "export_readable.py"

    if export_script.exists():
        result = subprocess.run(
            [sys.executable, str(export_script), jsonl_path_str, readable_dir],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"  ✓ Readable 导出: {readable_dir}/")
        else:
            print(f"  ⚠ Readable 导出失败: {result.stderr}")
    else:
        print(f"  ⚠ 未找到 export_readable.py，跳过 readable 导出")


if __name__ == "__main__":
    main()
