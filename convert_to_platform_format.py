#!/usr/bin/env python3
"""
将 singleturn 长上下文数据集转换为 inhouse 平台评估格式

用法:
    python convert_to_platform_format.py \
        --input instruct/singleturn_dataset.jsonl \
        --output platform_format/creative_longcontext.jsonl

输出格式符合平台要求:
    - data_id: 唯一标识
    - tags: [L1, L2, scenario]
    - L0/L1/L2/L3: 4层数据标签
    - query: 输入内容
    - ground_truth: 参考输出
    - judge_criteria: 评判标准
    - extra_info: 元数据
    - responses: {} (空字典，评估时填入)
"""

import argparse
import json
import os


def convert_to_platform(item, l0="创意评估", l2="长上下文"):
    """
    将 singleturn 格式转为平台格式

    Args:
        item: singleturn dataset 的单条数据
        l0: L0 专项名称
        l2: L2 大标签

    Returns:
        dict: 平台格式的数据
    """
    # 场景中文映射
    scenario_cn_map = {
        "nwa": "小说写作",
        "sd": "短剧编写",
        "nts": "小说改编"
    }

    scenario = item.get("scenario", "unknown")
    scenario_cn = scenario_cn_map.get(scenario, scenario)

    # 长度段标签
    length_bin = item.get("length_bin", "unknown")

    return {
        "data_id": item["id"],
        "benchmark_strategy_id": "creative_longcontext_llm_judge",  # 平台要求的策略ID
        "tags": [
            "单轮",
            "长上下文",
            scenario_cn,
            length_bin
        ],
        "L0": l0,
        "L1": "单轮",
        "L2": l2,
        "L3": "creative-longcontext",
        "query": item["input"],
        "ground_truth": item.get("reference_output", ""),
        "judge_criteria": item.get("judge_criteria", []),
        "extra_info": {
            "original_id": item["id"],
            "scenario": scenario,
            "scenario_cn": scenario_cn,
            "design_version": item.get("design_version", ""),
            "stage": item.get("stage", ""),
            "output_file": item.get("output_file", ""),
            "output_type": item.get("output_type", ""),
            "length_bin": length_bin,
            "input_tokens_est": item.get("input_tokens_est", 0),
            "reference_output_tokens_est": item.get("reference_output_tokens_est", 0),
            "has_judge_criteria": item.get("has_judge_criteria", False),
            "judge_criteria_count": item.get("judge_criteria_count", 0),
            "source_model": item.get("source_model", ""),
            "source_sample_id": item.get("source_sample_id", ""),
            "source_quality": item.get("source_quality", "")
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description="将 singleturn 数据集转换为 inhouse 平台格式"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="输入 JSONL 文件路径（如 instruct/singleturn_dataset.jsonl）"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="输出 JSONL 文件路径（如 platform_format/creative_longcontext.jsonl）"
    )
    parser.add_argument(
        "--l0",
        default="创意评估",
        help="L0 专项名称（默认: 创意评估）"
    )
    parser.add_argument(
        "--l2",
        default="长上下文",
        help="L2 大标签（默认: 长上下文）"
    )
    parser.add_argument(
        "--filter-scenario",
        help="只转换指定场景的数据（nwa/sd/nts），不指定则转换全部"
    )
    parser.add_argument(
        "--filter-length",
        help="只转换指定长度段的数据（如 40K-70K），不指定则转换全部"
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        help="最多转换的样本数（用于快速测试）"
    )

    args = parser.parse_args()

    # 读取输入
    with open(args.input, "r", encoding="utf-8") as f:
        items = [json.loads(line) for line in f]

    print(f"读取 {len(items)} 条原始数据")

    # 过滤
    if args.filter_scenario:
        items = [item for item in items if item.get("scenario") == args.filter_scenario]
        print(f"过滤场景后剩余 {len(items)} 条")

    if args.filter_length:
        items = [item for item in items if item.get("length_bin") == args.filter_length]
        print(f"过滤长度段后剩余 {len(items)} 条")

    if args.max_samples:
        items = items[:args.max_samples]
        print(f"限制样本数后剩余 {len(items)} 条")

    # 转换
    converted = []
    for item in items:
        converted.append(convert_to_platform(item, args.l0, args.l2))

    # 确保输出目录存在
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    # 写出
    with open(args.output, "w", encoding="utf-8") as f:
        for item in converted:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"\n转换完成: {len(converted)} 条数据 → {args.output}")

    # 统计信息
    from collections import Counter
    scenarios = Counter(item["extra_info"]["scenario"] for item in converted)
    lengths = Counter(item["extra_info"]["length_bin"] for item in converted)

    print(f"\n场景分布:")
    for scenario, count in scenarios.items():
        print(f"  {scenario}: {count}")

    print(f"\n长度分布:")
    for length, count in sorted(lengths.items()):
        print(f"  {length}: {count}")

    # 输出示例
    print(f"\n示例数据（第一条）:")
    print(json.dumps(converted[0], ensure_ascii=False, indent=2)[:1000] + "...")


if __name__ == "__main__":
    main()
