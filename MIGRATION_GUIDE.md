# 迁移到独立 Repo 指南

本文档说明如何将 `singleturn_longcontext_eval/` 从 universal_scenario_framework 中独立出来，成为 `creative-longcontext-eval` repo。

## 步骤 1: 创建新 Repo

在 GitHub 上创建新仓库：
```bash
# 仓库名称: creative-longcontext-eval
# 描述: Long-context evaluation framework for creative Agent scenarios
# Public/Private: 根据需要选择
# 初始化: 不勾选 README/LICENSE/.gitignore (我们会从本地推)
```

## 步骤 2: 准备本地目录

```bash
# 进入当前目录
cd /Users/feixiaoxu01/Documents/agents/agent_auto_evaluation/universal_scenario_framework/singleturn_longcontext_eval

# 初始化 git（如果还没有）
git init

# 添加 remote
git remote add origin https://github.com/feixiaoxu2022/creative-longcontext-eval.git
```

## 步骤 3: 整理文件结构

### 需要提交的文件

**核心脚本**（必须）:
```
build_singleturn_dataset.py       # 数据集构建（需要从 universal_scenario_framework 复制过来）
convert_to_pretrain.py            # Instruct → Pretrain 转换
run_inference_and_judge.py        # 推理 + 评判
export_readable.py                # 导出可读格式
```

**配置文件**（必须）:
```
README.md                         # 使用 README_NEW.md（已创建）
.gitignore                        # 已创建
system_prompts/*.md               # 各场景的系统提示模板
```

**数据集**（必须）:
```
instruct/singleturn_dataset.jsonl
instruct/singleturn_dataset_stats.md
pretrain/pretrain_dataset.jsonl
pretrain/pretrain_dataset_stats.md
```

**文档**（必须）:
```
docs/METHODOLOGY.md               # 已创建
docs/JUDGE_CRITERIA_DESIGN.md     # 待创建（可选）
docs/PRETRAIN_CONVERSION.md       # 待创建（可选）
```

**示例数据**（可选）:
```
example_data/nwa_sample.json      # 从 instruct/ 中抽取 1 条
example_data/sd_sample.json
example_data/nts_sample.json
```

### 不需要提交的文件

❌ **大文件/生成文件**（已在 .gitignore 中）:
```
eval_results/                     # 评测结果（用户自己跑）
*/readable/                       # 可读格式（可重新生成）
logs/                             # 日志
__pycache__/                      # Python 缓存
```

❌ **历史版本/备份**:
```
instruct/singleturn_dataset_sd_expanded.jsonl
instruct/singleturn_dataset_v1_with_invalid_checks.jsonl
pretrain/VALIDATION_REPORT.md     # 临时验证报告
```

❌ **源数据**（用户自己准备）:
```
source_data/                      # 不提交，用户从场景 repo 获取
```

## 步骤 4: 清理和重命名

```bash
# 使用新 README
mv README.md README_OLD.md
mv README_NEW.md README.md

# 删除历史版本数据集
rm instruct/singleturn_dataset_sd_expanded.jsonl
rm instruct/singleturn_dataset_v1_with_invalid_checks.jsonl
rm pretrain/VALIDATION_REPORT.md

# 创建占位目录（保证结构完整）
mkdir -p eval_results source_data example_data
touch eval_results/.gitkeep
touch source_data/.gitkeep

# 删除 readable 目录（过大，可重新生成）
rm -rf instruct/readable pretrain/readable
```

## 步骤 5: 提取示例数据（可选）

```bash
# 从 instruct 数据集中各抽取 1 条作为示例
python3 << 'EOF'
import json

scenarios = {"nwa": None, "sd": None, "nts": None}

with open("instruct/singleturn_dataset.jsonl") as f:
    for line in f:
        d = json.loads(line)
        s = d["scenario"]
        if scenarios[s] is None and d["length_bin"] == "20K-40K":  # 选中等长度的
            scenarios[s] = d

for s, data in scenarios.items():
    if data:
        with open(f"example_data/{s}_sample.json", "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✓ 已提取 {s} 示例")
EOF
```

## 步骤 6: 复制 build_singleturn_dataset.py

**注意**：`build_singleturn_dataset.py` 目前在 universal_scenario_framework 的其他位置，需要找到并复制过来。

```bash
# 查找该脚本
find /Users/feixiaoxu01/Documents/agents/agent_auto_evaluation/universal_scenario_framework -name "build_singleturn_dataset.py" -type f

# 复制到当前目录（假设在 scripts/ 下）
# cp ../scripts/build_singleturn_dataset.py .
```

**如果找不到该脚本**，需要重新编写或从 git 历史中恢复。

## 步骤 7: 首次提交

```bash
# 添加所有文件
git add .

# 检查将要提交的文件（确认无大文件/敏感信息）
git status

# 首次提交
git commit -m "Initial commit: Creative Long-Context Evaluation Framework

- Core scripts: build_singleturn_dataset.py, run_inference_and_judge.py, convert_to_pretrain.py
- Datasets: 150 instruct samples, 300 pretrain samples (NWA/SD/NTS)
- Documentation: README, METHODOLOGY, system prompts
- Length bins: <10K, 10K-20K, 20K-40K, 40K-70K, 70K-100K
"

# 推送到远程
git push -u origin main
```

## 步骤 8: 验证

在另一台机器上克隆并测试：

```bash
# 克隆
git clone https://github.com/feixiaoxu2022/creative-longcontext-eval.git
cd creative-longcontext-eval

# 检查文件完整性
ls -lh instruct/singleturn_dataset.jsonl  # 应该存在
ls -lh pretrain/pretrain_dataset.jsonl   # 应该存在

# 测试脚本（需要先准备 source_data/，见 README）
# python build_singleturn_dataset.py --help

# 测试推理（快速验证）
python run_inference_and_judge.py \
    --dataset instruct/singleturn_dataset.jsonl \
    --model-name claude-sonnet-4-6 \
    --base-url https://api.anthropic.com \
    --api-key $ANTHROPIC_API_KEY \
    --output-dir eval_results/test \
    --max-samples 2
```

## 步骤 9: 更新 universal_scenario_framework

在原 universal_scenario_framework repo 中：

1. **删除 singleturn_longcontext_eval/** 目录（已独立）
2. **更新 CLAUDE.md**：移除相关说明，添加链接指向新 repo
3. **提交变更**：
   ```bash
   git add singleturn_longcontext_eval/  # git rm
   git commit -m "refactor: 将长上下文评测框架独立到 creative-longcontext-eval repo"
   git push
   ```

## 注意事项

1. **数据集文件较大**（instruct 24MB, pretrain 39MB）
   - 确认 GitHub 可以接受（<100MB 无问题）
   - 如果超限，考虑用 Git LFS 或提供下载链接

2. **API Key 安全**
   - 检查所有文件确保没有硬编码的 API key
   - .gitignore 已包含 `.env` 和 `.env.local`

3. **依赖文档**
   - README 中已说明如何从场景 repo 获取源数据
   - 用户需要先 clone 场景 repo 才能构建新数据集

4. **持续维护**
   - 新场景数据发布时，更新数据集版本
   - Judge criteria 迭代时，更新文档说明

## Checklist

- [ ] 创建 GitHub repo
- [ ] 清理历史文件
- [ ] 重命名 README
- [ ] 复制 build_singleturn_dataset.py
- [ ] 提取示例数据
- [ ] 首次提交并推送
- [ ] 在另一台机器验证
- [ ] 更新 universal_scenario_framework
- [ ] 在新 repo 创建 Issues/Projects（可选）
- [ ] 添加 LICENSE 文件（建议 MIT）
