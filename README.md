# Creative Long-Context Evaluation

跨场景的创意类 Agent 长上下文评测框架，用于评估大模型在处理长文本创作任务时的能力表现。

## 📋 概述

本框架从三个创意类 Agent 评测场景（小说写作、短剧编写、小说改编短剧）的实际执行轨迹中提取长上下文评测数据，构建单轮推理+评判任务，系统性评估模型在不同长度段（<10K, 10K-20K, 20K-40K, 40K-70K, 70K-100K tokens）的表现。

### 核心特性

- **双模式支持**：Instruct 模式（含系统提示+任务指令）和 Pretrain 模式（纯续写）
- **多维度评判**：基于 LLM Judge 的语义质量评估（gate/basic/advanced 三层）
- **跨场景覆盖**：整合 NWA（小说写作）、SD（短剧）、NTS（小说改编）三个场景
- **长度分布均衡**：150 条 instruct 样本 / 300 条 pretrain 样本，覆盖 5 个长度段
- **可扩展设计**：支持新增场景、新增 judge_criteria、自定义评判标准

### 数据集统计

| 模式 | 样本数 | NWA | SD | NTS | 长度范围 |
|------|--------|-----|----|----|----------|
| **Instruct** | 150 | 29 | 97 | 24 | <10K ~ 100K |
| **Pretrain** | 300 | 128 | 138 | 34 | <10K ~ 100K |

## 🏗️ 架构

```
┌─────────────────────────────────────────────────────────────┐
│  场景 Repos (数据源)                                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ novel-writing-  │  │ shortdrama-eval │  │ novel-to-    │ │
│  │ alchemist       │  │                 │  │ script       │ │
│  │ evaluation_     │  │ evaluation_     │  │ evaluation_  │ │
│  │ outputs/        │  │ outputs/        │  │ outputs/     │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  数据集构建 (build_singleturn_dataset.py)                    │
│  - 提取轨迹中的 input、reference_output、judge_criteria     │
│  - 估算 token 数、分配长度段                                  │
│  - 生成 instruct/singleturn_dataset.jsonl                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
          ┌───────────────────┴───────────────────┐
          ↓                                       ↓
┌──────────────────────┐              ┌──────────────────────┐
│  Instruct 模式        │              │  Pretrain 模式        │
│  (带指令+参考文档)    │─────────────→│  (纯文本续写)        │
│  150 条               │  convert_to_ │  300 条              │
│                      │  pretrain.py │                      │
└──────────────────────┘              └──────────────────────┘
          ↓                                       ↓
┌─────────────────────────────────────────────────────────────┐
│  模型推理 + Judge 评判 (run_inference_and_judge.py)          │
│  - 调用模型 API 生成输出                                      │
│  - 使用 LLM Judge 对比 reference_output 评分                │
│  - 输出 inference result + judge scores                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  评测结果分析                                                 │
│  - 按长度段统计推理成功率、平均分数                           │
│  - 识别模型在不同长度下的性能衰减点                           │
│  - 生成可读格式报告 (export_readable.py)                     │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 快速开始

### 前置要求

- Python 3.8+
- 依赖包：`litellm`, `pandas`, `tabulate`, `tiktoken`

```bash
pip install litellm pandas tabulate tiktoken
```

### 步骤 1: 准备源数据

从各场景 repo 获取 `evaluation_outputs/` 目录：

```bash
# 创建源数据目录
mkdir -p source_data/{nwa_dsv1,nwa_dsv2,sd,nts}

# 从各场景 repo 复制（或通过 HTTP API 下载）
# NWA dsv1
cp -r path/to/novel-writing-alchemist/evaluation_outputs/eval_dsv1_* source_data/nwa_dsv1/

# NWA dsv2
cp -r path/to/novel-writing-alchemist/evaluation_outputs/eval_dsv2_* source_data/nwa_dsv2/

# SD
cp -r path/to/shortdrama-eval/evaluation_outputs/eval_dsv3_* source_data/sd/

# NTS
cp -r path/to/novel-to-script/evaluation_outputs/eval_nts_v3_* source_data/nts/
```

**数据格式要求**：每个样本目录需包含：
- `{sample_id}.json` - 执行结果（含 `input`, `reference_output`, `judge_criteria`）
- `{sample_id}_env/` - 环境文件（可选，用于重现）

### 步骤 2: 构建数据集

```bash
# 构建 Instruct 模式数据集
python build_singleturn_dataset.py \
    --nwa-dsv1 source_data/nwa_dsv1/ \
    --nwa-dsv2 source_data/nwa_dsv2/ \
    --sd source_data/sd/ \
    --nts source_data/nts/ \
    --output instruct/singleturn_dataset.jsonl

# 转换为 Pretrain 模式（去除指令，只保留已有正文）
python convert_to_pretrain.py \
    --input instruct/singleturn_dataset.jsonl \
    --output pretrain/pretrain_dataset.jsonl
```

### 步骤 3: 运行评测

```bash
# Instruct 模式
python run_inference_and_judge.py \
    --dataset instruct/singleturn_dataset.jsonl \
    --model-name claude-opus-4-6 \
    --base-url https://api.anthropic.com \
    --api-key $ANTHROPIC_API_KEY \
    --output-dir eval_results/claude_instruct \
    --judge-model claude-sonnet-4-6

# Pretrain 模式
python run_inference_and_judge.py \
    --dataset pretrain/pretrain_dataset.jsonl \
    --model-name glm-5-plus \
    --base-url https://open.bigmodel.cn/api/paas/v4 \
    --api-key $GLM_API_KEY \
    --output-dir eval_results/glm_pretrain \
    --judge-model claude-sonnet-4-6
```

**支持的参数**：
- `--max-samples N` - 只跑前 N 条样本（快速测试）
- `--resume` - 断点续跑（跳过已有结果）
- `--parallel N` - 并发数（默认 1）
- `--system-prompt-file` - 自定义系统提示（可选）

### 步骤 4: 分析结果

```bash
# 导出可读格式
python export_readable.py \
    --result-dir eval_results/claude_instruct \
    --output-dir eval_results/claude_instruct/readable

# 统计推理成功率和平均分数（按长度段）
python analyze_results.py \
    --result-dir eval_results/claude_instruct \
    --output eval_results/claude_instruct/analysis.md
```

## 📊 数据集格式

### Instruct 模式样本

```jsonc
{
  "id": "nwa_dsv2_claude-opus-4-6_NW_CLEAR_MEDIUM_SWEET_001_chapter_23",
  "scenario": "nwa",
  "design_version": "dsv2",
  "source_model": "claude-opus-4-6",
  "source_sample_id": "NW_CLEAR_MEDIUM_SWEET_001",
  "stage": "chapter_writing",
  "output_file": "chapters/chapter_23.md",
  "input_tokens_est": 45203,
  "length_bin": "40K-70K",
  "has_judge_criteria": true,
  "judge_criteria_count": 8,
  "input": "# 系统设定\n...\n# 用户需求\n...\n# 参考文档\n...\n# 已有创作成果\n...\n# 当前任务\n...",
  "reference_output": "# 第二十三章 ...",
  "reference_output_tokens_est": 3521,
  "judge_criteria": [
    {
      "check_name": "故事推进合理性",
      "criteria_text": "...",
      "tier": "basic"
    }
  ]
}
```

### Pretrain 模式样本

```jsonc
{
  "id": "nwa_dsv2_claude-opus-4-6_NW_CLEAR_MEDIUM_SWEET_001_chapter_23",
  "scenario": "nwa",
  "input_tokens_est": 41682,  // 减少（去掉了指令部分）
  "length_bin": "40K-70K",
  "judge_criteria_count": 8,
  "input": "# 第一章 ...\n# 第二章 ...\n...\n# 第二十二章 ...",  // 只保留已完成章节
  "judge_criteria": [...],  // 评判标准保持不变
  // reference_output 已删除（Pretrain 模式不需要）
}
```

## 🎯 评判标准设计

每个场景有专属的 `judge_criteria` 定义，分为三层：

| Tier | 含义 | 不通过影响 | 示例 |
|------|------|-----------|------|
| **gate** | 门槛项 | 整体质量判定为不合格 | 格式正确、无乱码、基本逻辑通顺 |
| **basic** | 基础质量 | 降低 content_score | 角色行为符合人设、台词信息密度合理 |
| **advanced** | 高级质量 | 影响较小 | 镜头语言丰富、情感张力强 |

**评分逻辑**：
```python
if any(gate_check fails):
    quality_level = "unqualified"
else:
    content_score = weighted_avg(basic + advanced checks)
    quality_level = "good" if content_score >= 75 else "qualified"
```

## 📁 目录结构

```
creative-longcontext-eval/
├── README.md                          # 本文档
├── build_singleturn_dataset.py       # 数据集构建脚本
├── convert_to_pretrain.py            # Instruct → Pretrain 转换
├── run_inference_and_judge.py        # 推理 + 评判
├── export_readable.py                # 导出可读格式
├── analyze_results.py                # 结果分析（待实现）
├── instruct/                          # Instruct 模式数据集
│   ├── singleturn_dataset.jsonl
│   └── singleturn_dataset_stats.md
├── pretrain/                          # Pretrain 模式数据集
│   ├── pretrain_dataset.jsonl
│   └── pretrain_dataset_stats.md
├── system_prompts/                    # 各场景系统提示模板
│   ├── nwa_dsv1.md
│   ├── nwa_dsv2.md
│   ├── sd.md
│   └── nts.md
├── eval_results/                      # 评测结果输出目录
│   └── run_YYYYMMDD_HHMMSS_{model}/
│       ├── {sample_id}.json           # 单样本结果
│       └── summary.json               # 汇总统计
├── docs/                              # 方法论文档
│   ├── METHODOLOGY.md                 # 长上下文评测方法论
│   ├── JUDGE_CRITERIA_DESIGN.md       # Judge criteria 设计原则
│   └── PRETRAIN_CONVERSION.md         # Pretrain 转换说明
└── example_data/                      # 示例数据（可选）
    ├── nwa_sample.json
    ├── sd_sample.json
    └── nts_sample.json
```

## 🔧 高级用法

### 自定义 Judge Criteria

在构建数据集时，可以通过修改源场景的 `judge_criteria` 定义来调整评判标准：

```python
# 在 build_singleturn_dataset.py 中添加/修改 criteria
custom_criteria = [
    {
        "check_name": "自定义检查项",
        "criteria_text": "评判标准描述...",
        "tier": "basic"  # gate / basic / advanced
    }
]
```

### 支持新场景

1. 准备新场景的 `evaluation_outputs/` 数据
2. 在 `build_singleturn_dataset.py` 中添加场景配置
3. 在 `system_prompts/` 下添加新场景的系统提示模板
4. 重新构建数据集

### 使用本地模型

```bash
# 使用 vLLM / Ollama 等本地服务
python run_inference_and_judge.py \
    --dataset instruct/singleturn_dataset.jsonl \
    --model-name qwen2.5-72b-instruct \
    --base-url http://localhost:8000/v1 \
    --api-key none \
    --output-dir eval_results/qwen_local
```

## 📖 相关场景 Repos

本框架的数据来源于以下三个创意类 Agent 评测场景：

- [novel-writing-alchemist](https://github.com/feixiaoxu2022/novel-writing-alchemist) - 小说写作场景（NWA）
- [shortdrama-eval](https://github.com/feixiaoxu2022/shortdrama-eval) - 短剧编写场景（SD）
- [novel-to-script](https://github.com/feixiaoxu2022/novel-to-script) - 小说改编短剧场景（NTS）

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

**需要帮助的方向**：
- 新增更多创意类场景的数据
- 优化 Judge Criteria 设计
- 支持更多模型 API（Gemini、Claude、国产模型等）
- 改进结果分析和可视化

## 📄 许可证

MIT License

## 📧 联系方式

如有问题或建议，请提交 Issue 或联系维护者。
