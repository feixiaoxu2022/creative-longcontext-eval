#!/usr/bin/env python3
"""
单轮长上下文数据集 — 推理 + Judge 打分验证

从数据集中抽取样本，调用被测模型做推理（input → model_output），
再用 LLM Judge 对 model_output 逐条 criteria 打分。

用法：
    # 对 3 个模型各跑 5 条，验证 judge 可靠性
    python3 run_inference_and_judge.py \
        --dataset singleturn_dataset.jsonl \
        --models claude-opus-4-6,doubao-seed-2-0-pro-260215,ernie-5.0-thinking-preview \
        --sample-count 5 \
        --output-dir eval_results/

输出：
    eval_results/
      {model}/
        {item_id}.json — 包含 model_output + judge_results
      summary.json — 汇总统计
"""

import argparse
import json
import os
import random
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

import litellm
litellm.suppress_debug_info = True
litellm.set_verbose = False
from litellm import completion

# 线程安全的打印锁
print_lock = threading.Lock()


# ── 模型 API 配置 ──

MODEL_CONFIGS = {
    "claude-opus-4-6": {
        "api_base": "http://yy.dbh.baidu-int.com/v1",
        "api_key": "sk-9l6YZYau2dgCoziKh6bWNkF0p1ho5mSVHz39jZivtMTmb48i",
    },
    "gemini-3-pro-preview": {
        "api_base": "http://yy.dbh.baidu-int.com/v1",
        "api_key": "sk-9l6YZYau2dgCoziKh6bWNkF0p1ho5mSVHz39jZivtMTmb48i",
    },
    "doubao-seed-2-0-pro-260215": {
        "api_base": "http://yy.dbh.baidu-int.com/v1",
        "api_key": "sk-9l6YZYau2dgCoziKh6bWNkF0p1ho5mSVHz39jZivtMTmb48i",
    },
    "ernie-5.0-thinking-preview": {
        "api_base": "https://qianfan.baidubce.com/v2",
        "api_key": "bce-v3/ALTAK-mCOi62yEOQCJIvZVDI521/10000568a22b656d14d37bb80abb5da439026f1a",
    },
    "glm-5": {
        "api_base": "https://open.bigmodel.cn/api/paas/v4",
        "api_key": "fc0dc81d18124abea8da832af681401b.QsiurjETpUArzi4C",
    },
}

# Judge 用的模型
JUDGE_MODEL = "gpt-5.2"
JUDGE_API_BASE = "http://yy.dbh.baidu-int.com/v1"
JUDGE_API_KEY = "sk-9l6YZYau2dgCoziKh6bWNkF0p1ho5mSVHz39jZivtMTmb48i"


# ── LLM 调用 ──

def safe_print(*args, **kwargs):
    """线程安全的打印"""
    with print_lock:
        print(*args, **kwargs)


def call_llm(messages, model_name, api_base, api_key, response_format=None, max_retries=5):
    """调用 LLM，带重试"""
    last_error = None
    for attempt in range(max_retries):
        try:
            kwargs = {
                "model": model_name,
                "messages": messages,
                "api_base": api_base,
                "api_key": api_key,
                "custom_llm_provider": "openai",
            }
            if response_format:
                kwargs["response_format"] = response_format

            response = completion(**kwargs)
            choice = response.choices[0]
            content = choice.message.content
            usage = response.usage

            # 提取详细信息用于判断截断
            result = {
                "success": True,
                "content": content,
                "input_tokens": usage.prompt_tokens if usage else 0,
                "output_tokens": usage.completion_tokens if usage else 0,
                "finish_reason": choice.finish_reason if hasattr(choice, 'finish_reason') else None,
                "error": None,
            }

            # Ernie thinking 模型的 reasoning_content
            if hasattr(choice.message, 'reasoning_content'):
                result["reasoning_content"] = choice.message.reasoning_content
                result["reasoning_tokens"] = usage.completion_tokens_details.reasoning_tokens if hasattr(usage, 'completion_tokens_details') else 0

            return result
        except Exception as e:
            last_error = {
                "type": type(e).__name__,
                "message": str(e),
                "attempt": attempt + 1,
            }
            safe_print(f"  [重试 {attempt+1}/{max_retries}] {model_name}: {type(e).__name__}: {str(e)[:200]}", file=sys.stderr)
            if attempt < max_retries - 1:
                time.sleep(min(5 * (2 ** attempt), 60))
    return {
        "success": False,
        "content": "",
        "input_tokens": 0,
        "output_tokens": 0,
        "error": last_error,
    }


# ── 推理 ──

def run_inference(item, model_name, api_base, api_key):
    """对一条数据做推理"""
    input_text = item["input"]
    messages = [{"role": "user", "content": input_text}]

    safe_print(f"  推理 {item['id'][:60]}... (input ~{item['input_tokens_est']:,} tokens)", file=sys.stderr)
    result = call_llm(messages, model_name, api_base, api_key)
    if result["success"]:
        safe_print(f"  ✓ 输出 {result['output_tokens']} tokens", file=sys.stderr)
    else:
        error_info = result.get("error", {})
        safe_print(f"  ✗ 推理失败: {error_info.get('type', 'Unknown')}: {error_info.get('message', '')[:100]}", file=sys.stderr)
    return result


# ── Judge 打分 ──

def extract_judge_context(input_text: str, max_context_chars: int = 8000) -> str:
    """
    从 input 中提取 judge 需要的关键上下文，跳过大体积的纯文档部分。

    提取策略（按三个场景通用结构）：
    1. 系统设定 + 用户需求（任务定义和要求）
    2. 已有创作成果（人物/大纲等结构化数据，跳过参考文档写作指南）
       - 对此段设置字数上限，超出则截断
    3. 当前任务（末尾的具体指令）

    fallback：找不到结构标记时，取 input 末尾 max_context_chars 字符。
    """
    def find_pos(text, markers):
        for m in markers:
            idx = text.find(m)
            if idx != -1:
                return idx
        return -1

    pos_user_req   = find_pos(input_text, ["# 用户需求", "## 用户需求"])
    pos_ref_doc    = find_pos(input_text, ["# 参考文档", "## 参考文档"])
    pos_creation   = find_pos(input_text, ["# 已有创作成果", "## 已有创作成果", "# 已完成创作"])
    pos_chapters   = find_pos(input_text, ["## 已完成章节", "# 已完成章节", "## 已完成剧本", "# 已完成集数"])
    pos_cur_task   = find_pos(input_text, ["# 当前任务", "## 当前任务"])

    parts = []

    # 1. 系统设定 + 用户需求（从头到参考文档开始）
    end_of_req = pos_ref_doc if pos_ref_doc != -1 else (pos_creation if pos_creation != -1 else len(input_text))
    if end_of_req > 0:
        parts.append(input_text[:end_of_req].strip())

    # 2. 已有创作成果（跳过参考文档，取创作成果到已完成章节之间的结构化数据）
    if pos_creation != -1:
        end_of_creation = pos_chapters if pos_chapters != -1 else (pos_cur_task if pos_cur_task != -1 else len(input_text))
        creation_text = input_text[pos_creation:end_of_creation].strip()
        # 对创作成果段设置字数上限，避免超长 outline 撑爆 judge context
        creation_budget = max_context_chars - sum(len(p) for p in parts) - 500  # 留 500 给当前任务
        if len(creation_text) > creation_budget > 0:
            creation_text = creation_text[:creation_budget] + "\n...[内容过长，已截断]"
        parts.append(creation_text)

    # 3. 当前任务
    if pos_cur_task != -1:
        parts.append(input_text[pos_cur_task:].strip())
    elif pos_chapters != -1:
        # fallback：取最后一段（可能是章节末尾的任务说明）
        parts.append(input_text[-(min(500, len(input_text))):].strip())

    if parts:
        return "\n\n---\n\n".join(parts)

    # 最终 fallback：取末尾
    return input_text[-max_context_chars:].strip()


def judge_single_criteria(input_text, model_output, criteria, judge_model, judge_api_base, judge_api_key):
    """用 LLM Judge 对一条 criteria 打分"""
    context = extract_judge_context(input_text)
    prompt = f"""请评估以下模型输出是否符合业务标准。

**输入上下文（任务定义、创作设定、当前指令）：**
{context}

**业务标准：**
{criteria['criteria_text']}

**待评估的模型输出：**
{model_output}

⚠️ 重要说明：
- 内容可能是JSON格式，也可能不是，请关注语义本身，不要因格式问题影响评估
- 如果内容被截断，请基于可见部分进行合理推断
- 重点评估内容质量，而非格式规范

请以JSON格式回复：
{{"matched": true/false, "reason": "详细说明评估依据，包括具体的优点或不足"}}"""

    result = call_llm(
        [{"role": "user", "content": prompt}],
        judge_model, judge_api_base, judge_api_key,
        response_format={"type": "json_object"},
    )

    if result["success"]:
        try:
            parsed = json.loads(result["content"])
            return {
                "criteria_name": criteria["name"],
                "criteria_tier": criteria["tier"],
                "matched": parsed.get("matched", False),
                "reason": parsed.get("reason", ""),
                "judge_tokens": result["input_tokens"] + result["output_tokens"],
            }
        except json.JSONDecodeError:
            return {
                "criteria_name": criteria["name"],
                "criteria_tier": criteria["tier"],
                "matched": False,
                "reason": f"Judge 响应解析失败: {result['content'][:200]}",
                "judge_tokens": 0,
            }
    return {
        "criteria_name": criteria["name"],
        "criteria_tier": criteria["tier"],
        "matched": False,
        "reason": "Judge 调用失败",
        "judge_tokens": 0,
    }


def run_judge(item, model_output, judge_model, judge_api_base, judge_api_key):
    """对推理结果做全量 judge 打分"""
    criteria_list = item.get("judge_criteria", [])
    if not criteria_list:
        return []

    input_text = item.get("input", "")
    results = []
    for i, criteria in enumerate(criteria_list):
        safe_print(f"    Judge [{i+1}/{len(criteria_list)}] {criteria['name']}...", file=sys.stderr)
        result = judge_single_criteria(
            input_text, model_output, criteria, judge_model, judge_api_base, judge_api_key
        )
        results.append(result)
        # 降低 judge QPS
        time.sleep(1)

    passed = sum(1 for r in results if r["matched"])
    total = len(results)
    safe_print(f"    Judge 结果: {passed}/{total} 通过", file=sys.stderr)
    return results


# ── 并行处理单个样本 ──

def process_single_sample(item, model_name, config, model_dir, args):
    """处理单个样本的推理+judge（用于并行调用）"""
    result_path = os.path.join(model_dir, f"{item['id'][:80].replace('/', '_')}.json")

    # 检查是否已有结果（resume）
    if os.path.exists(result_path):
        with open(result_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
        if existing.get("inference_success") and existing.get("judge_results"):
            safe_print(f"  [{model_name}] {item['id'][:60]} (已有结果，跳过)", file=sys.stderr)
            return existing

    safe_print(f"  [{model_name}] 开始处理 {item['id'][:60]}", file=sys.stderr)

    # 推理
    if args.skip_inference and os.path.exists(result_path):
        with open(result_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
        model_output = existing.get("model_output", "")
        inference_success = existing.get("inference_success", False)
        output_tokens = existing.get("output_tokens", 0)
        inference_error = existing.get("error")
    else:
        inf_result = run_inference(item, model_name, config["api_base"], config["api_key"])
        model_output = inf_result["content"]
        inference_success = inf_result["success"]
        output_tokens = inf_result["output_tokens"]
        inference_error = inf_result.get("error")
        finish_reason = inf_result.get("finish_reason")
        reasoning_content = inf_result.get("reasoning_content")
        reasoning_tokens = inf_result.get("reasoning_tokens", 0)

    # Judge
    judge_results = []
    if inference_success and model_output:
        judge_results = run_judge(
            item, model_output, args.judge_model, JUDGE_API_BASE, JUDGE_API_KEY
        )

    # 保存
    result = {
        "item_id": item["id"],
        "scenario": item["scenario"],
        "stage": item["stage"],
        "output_type": item.get("output_type", ""),
        "length_bin": item["length_bin"],
        "input_tokens_est": item["input_tokens_est"],
        "tested_model": model_name,
        "inference_success": inference_success,
        "output_tokens": output_tokens,
        "model_output": model_output[:50000],  # 截断防止过大
        "judge_model": args.judge_model,
        "judge_results": judge_results,
        "judge_pass_count": sum(1 for jr in judge_results if jr.get("matched")),
        "judge_total_count": len(judge_results),
    }

    # 添加推理详情（用于异常分析）
    if inference_success:
        if finish_reason:
            result["finish_reason"] = finish_reason
        if reasoning_content:
            result["reasoning_content"] = reasoning_content[:5000]  # 截断
            result["reasoning_tokens"] = reasoning_tokens
    else:
        # 推理失败,添加错误信息
        if inference_error:
            result["error"] = inference_error

    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    safe_print(f"  [{model_name}] ✓ 完成 {item['id'][:60]} ({result['judge_pass_count']}/{result['judge_total_count']} 通过)", file=sys.stderr)
    return result


def process_model(model_name, samples, config, args):
    """处理单个模型的所有样本（用于并行调用）"""
    safe_print(f"\n{'='*60}", file=sys.stderr)
    safe_print(f"模型: {model_name}", file=sys.stderr)
    safe_print(f"{'='*60}", file=sys.stderr)

    model_dir = os.path.join(args.output_dir, model_name.replace("/", "_"))
    os.makedirs(model_dir, exist_ok=True)

    # 样本级并行
    model_results = []
    max_workers = min(args.sample_workers, len(samples))

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_single_sample, item, model_name, config, model_dir, args): item
            for item in samples
        }

        for future in as_completed(futures):
            try:
                result = future.result()
                model_results.append(result)
            except Exception as e:
                item = futures[future]
                safe_print(f"  [{model_name}] ✗ 处理失败 {item['id'][:60]}: {str(e)}", file=sys.stderr)

    return model_name, model_results


# ── 采样 ──

def select_samples(dataset, sample_count, seed=42):
    """从数据集中采样，优先选有 judge_criteria 且长度多样的"""
    random.seed(seed)
    eligible = [item for item in dataset if item.get("judge_criteria")]

    # 按 length_bin 分组均匀采样
    from collections import defaultdict
    by_bin = defaultdict(list)
    for item in eligible:
        by_bin[item["length_bin"]].append(item)

    per_bin = max(1, sample_count // len(by_bin))
    selected = []
    for bin_name in sorted(by_bin.keys()):
        pool = by_bin[bin_name]
        random.shuffle(pool)
        selected.extend(pool[:per_bin])

    # 补齐
    if len(selected) < sample_count:
        remaining = [item for item in eligible if item not in selected]
        random.shuffle(remaining)
        selected.extend(remaining[:sample_count - len(selected)])

    return selected[:sample_count]


# ── 汇总 ──

def generate_summary(all_results):
    """生成汇总统计"""
    summary = {
        "total_items": 0,
        "by_model": {},
    }

    for model_name, results in all_results.items():
        model_stats = {
            "items_count": len(results),
            "inference_success": sum(1 for r in results if r.get("inference_success")),
            "judge_results": {
                "total_criteria": 0,
                "passed": 0,
                "failed": 0,
                "by_tier": {"basic": {"total": 0, "passed": 0}, "advanced": {"total": 0, "passed": 0}},
            },
            "avg_inference_tokens": 0,
        }

        total_output_tokens = 0
        for r in results:
            if r.get("inference_success"):
                total_output_tokens += r.get("output_tokens", 0)
            for jr in r.get("judge_results", []):
                model_stats["judge_results"]["total_criteria"] += 1
                tier = jr.get("criteria_tier", "basic")
                if tier not in model_stats["judge_results"]["by_tier"]:
                    model_stats["judge_results"]["by_tier"][tier] = {"total": 0, "passed": 0}
                model_stats["judge_results"]["by_tier"][tier]["total"] += 1
                if jr.get("matched"):
                    model_stats["judge_results"]["passed"] += 1
                    model_stats["judge_results"]["by_tier"][tier]["passed"] += 1
                else:
                    model_stats["judge_results"]["failed"] += 1

        inf_count = model_stats["inference_success"]
        model_stats["avg_inference_tokens"] = total_output_tokens // inf_count if inf_count else 0

        jt = model_stats["judge_results"]["total_criteria"]
        jp = model_stats["judge_results"]["passed"]
        model_stats["judge_results"]["pass_rate"] = f"{jp/jt*100:.1f}%" if jt > 0 else "N/A"

        for tier, ts in model_stats["judge_results"]["by_tier"].items():
            ts["pass_rate"] = f"{ts['passed']/ts['total']*100:.1f}%" if ts["total"] > 0 else "N/A"

        summary["by_model"][model_name] = model_stats
        summary["total_items"] += len(results)

    return summary


# ── 主流程 ──

def main():
    parser = argparse.ArgumentParser(description="单轮数据集推理+Judge打分验证（并行版本）")
    parser.add_argument("--dataset", required=True, help="数据集 JSONL 路径")
    parser.add_argument("--models", required=True, help="被测模型，逗号分隔")
    parser.add_argument("--sample-count", type=int, default=5, help="每个模型抽取的样本数")
    parser.add_argument("--output-dir", default="eval_results", help="输出目录")
    parser.add_argument("--judge-model", default=JUDGE_MODEL, help="Judge 模型名")
    parser.add_argument("--skip-inference", action="store_true", help="跳过推理，只做 judge（需要已有推理结果）")
    parser.add_argument("--seed", type=int, default=42, help="随机种子")
    parser.add_argument("--model-workers", type=int, default=3, help="模型级并行数（默认3）")
    parser.add_argument("--sample-workers", type=int, default=5, help="样本级并行数（默认5）")
    args = parser.parse_args()

    # 加载数据集
    dataset = []
    with open(args.dataset, "r", encoding="utf-8") as f:
        for line in f:
            dataset.append(json.loads(line))
    safe_print(f"加载 {len(dataset)} 条数据", file=sys.stderr)

    models = [m.strip() for m in args.models.split(",")]
    valid_models = []
    for m in models:
        if m not in MODEL_CONFIGS:
            safe_print(f"警告: 模型 '{m}' 无 API 配置，跳过", file=sys.stderr)
        else:
            valid_models.append(m)

    if not valid_models:
        safe_print("错误: 没有有效的模型", file=sys.stderr)
        sys.exit(1)

    # 采样
    samples = select_samples(dataset, args.sample_count, seed=args.seed)
    safe_print(f"采样 {len(samples)} 条 (bins: {', '.join(set(s['length_bin'] for s in samples))})", file=sys.stderr)

    os.makedirs(args.output_dir, exist_ok=True)

    all_results = {}

    # 模型级并行
    max_workers = min(args.model_workers, len(valid_models))
    safe_print(f"\n开始并行评测: {len(valid_models)} 个模型, {len(samples)} 个样本", file=sys.stderr)
    safe_print(f"并行配置: 模型级 {max_workers} workers, 样本级 {args.sample_workers} workers", file=sys.stderr)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_model, model_name, samples, MODEL_CONFIGS[model_name], args): model_name
            for model_name in valid_models
        }

        for future in as_completed(futures):
            model_name = futures[future]
            try:
                returned_model_name, model_results = future.result()
                all_results[returned_model_name] = model_results
                safe_print(f"\n✓ 模型 {returned_model_name} 完成: {len(model_results)} 个样本", file=sys.stderr)
            except Exception as e:
                safe_print(f"\n✗ 模型 {model_name} 失败: {str(e)}", file=sys.stderr)

    # 汇总
    summary = generate_summary(all_results)
    summary_path = os.path.join(args.output_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    # 打印汇总
    safe_print(f"\n{'='*60}", file=sys.stderr)
    safe_print("汇总结果", file=sys.stderr)
    safe_print(f"{'='*60}", file=sys.stderr)
    for model_name, stats in summary["by_model"].items():
        jr = stats["judge_results"]
        safe_print(f"\n{model_name}:", file=sys.stderr)
        safe_print(f"  推理成功: {stats['inference_success']}/{stats['items_count']}", file=sys.stderr)
        safe_print(f"  平均输出 tokens: {stats['avg_inference_tokens']}", file=sys.stderr)
        safe_print(f"  Judge 通过率: {jr['pass_rate']} ({jr['passed']}/{jr['total_criteria']})", file=sys.stderr)
        for tier, ts in jr["by_tier"].items():
            safe_print(f"    {tier}: {ts['pass_rate']} ({ts['passed']}/{ts['total']})", file=sys.stderr)

    safe_print(f"\n结果保存到 {args.output_dir}/", file=sys.stderr)


if __name__ == "__main__":
    main()
