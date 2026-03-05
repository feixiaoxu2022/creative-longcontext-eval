# 单轮长上下文评测数据集统计报告

**生成时间**: 2026-03-04
**总条数**: 150
**数据集文件**: `singleturn_dataset.jsonl` (45MB)

## 1. 输入长度分布

| 长度区间 | 条数 | 占比 | 平均tokens | 最小tokens | 最大tokens |
|----------|------|------|-----------|-----------|-----------|
| 10K-20K | 30 | 20.0% | 13,216 | 10,323 | 19,222 |
| 20K-40K | 40 | 26.7% | 24,916 | 20,064 | 35,692 |
| 40K-70K | 50 | 33.3% | 48,360 | 40,169 | 64,108 |
| 70K-100K | 30 | 20.0% | 84,464 | 70,407 | 124,386 |

**全局**: min=10,323, max=124,386, avg=42,300, median=40,854

## 2. 产出物类型分布

| 产出物类型 | 条数 | 占比 |
|-----------|------|------|
| 小说章节 | 80 | 53.3% |
| 原创剧本 | 54 | 36.0% |
| 改编剧本 | 11 | 7.3% |
| 拆书分析 | 3 | 2.0% |
| 分集大纲 | 2 | 1.3% |

## 3. 场景分布

| 场景 | 条数 | 占比 |
|------|------|------|
| NWA 小说创作 | 80 | 53.3% |
| SD 短剧创作 | 56 | 37.3% |
| NTS 小说改编剧本 | 14 | 9.3% |

## 4. 阶段分布

| 阶段 | 条数 | 占比 |
|------|------|------|
| chapter_writing | 80 | 53.3% |
| script_writing | 65 | 43.3% |
| analysis | 3 | 2.0% |
| outline | 2 | 1.3% |

## 5. 题材分布

| 场景/题材 | 条数 | 占比 |
|----------|------|------|
| nwa/sweet | 18 | 12.0% |
| nwa/angsty | 15 | 10.0% |
| nwa/suspense | 14 | 9.3% |
| sd/revenge_drama | 10 | 6.7% |
| sd/transmigration | 10 | 6.7% |
| sd/family_saga | 10 | 6.7% |
| nwa/neutral | 9 | 6.0% |
| nwa/adventure | 9 | 6.0% |
| sd/underdog_comeback | 9 | 6.0% |
| nwa/sweet_drama | 7 | 4.7% |
| sd/mystery_thriller | 7 | 4.7% |
| sd/sweet_romance | 6 | 4.0% |
| nwa/brainy_action | 4 | 2.7% |
| nts/entertainment | 4 | 2.7% |
| sd/son_in_law | 4 | 2.7% |
| nwa/heroine | 4 | 2.7% |
| nts/school_sweet | 2 | 1.3% |
| nts/scifi | 2 | 1.3% |
| nts/xianxia | 2 | 1.3% |
| nts/historical | 2 | 1.3% |
| nts/survival_game | 1 | 0.7% |
| nts/urban_fantasy | 1 | 0.7% |

## 6. 来源模型分布

| 模型 | 质量等级 | 条数 | 占比 |
|------|---------|------|------|
| MiniMax-M2.5 | mixed | 29 | 19.3% |
| claude-opus-4-5-20251101 | high | 22 | 14.7% |
| claude-opus-4-6 | high | 21 | 14.0% |
| glm-5 | mixed | 21 | 14.0% |
| doubao-seed-2-0-pro-260215 | mixed | 9 | 6.0% |
| ernie-5.0-thinking-preview | mixed | 9 | 6.0% |
| kimi-k2.5 | mixed | 9 | 6.0% |
| qwen3-max-2026-01-23 | mixed | 9 | 6.0% |
| qwen3.5-plus-2026-02-15 | mixed | 9 | 6.0% |
| gemini-3-pro-preview | high | 7 | 4.7% |
| openai/EB5-0209-A35B-midtrain-128k-chat | mixed | 5 | 3.3% |

**来源质量汇总**: high=50 (33%), mixed=100 (67%)

## 7. 模型 × 长度区间 交叉表

| 模型 | 10K-20K | 20K-40K | 40K-70K | 70K-100K | 合计 |
|------|------|------|------|------|------|
| MiniMax-M2.5 | 6 | 7 | 10 | 6 | 29 |
| claude-opus-4-5-20251101 | 4 | 4 | 10 | 4 | 22 |
| claude-opus-4-6 | 3 | 4 | 7 | 7 | 21 |
| glm-5 | 2 | 3 | 4 | 12 | 21 |
| doubao-seed-2-0-pro-260215 | 2 | 3 | 4 | 0 | 9 |
| ernie-5.0-thinking-preview | 2 | 3 | 4 | 0 | 9 |
| kimi-k2.5 | 2 | 3 | 4 | 0 | 9 |
| qwen3-max-2026-01-23 | 2 | 3 | 3 | 1 | 9 |
| qwen3.5-plus-2026-02-15 | 2 | 3 | 4 | 0 | 9 |
| gemini-3-pro-preview | 3 | 4 | 0 | 0 | 7 |
| openai/EB5-0209-A35B-midtrain-128k-chat | 2 | 3 | 0 | 0 | 5 |

## 8. Reference Output 长度分布

- **min**: 225 tokens
- **max**: 9,391 tokens
- **avg**: 1,687 tokens
- **median**: 1,353 tokens

| 区间 | 条数 | 占比 |
|------|------|------|
| <1K | 51 | 34.0% |
| 1K-3K | 82 | 54.7% |
| 3K-5K | 14 | 9.3% |
| 5K-10K | 3 | 2.0% |
| >10K | 0 | 0.0% |

## 9. Judge Criteria 覆盖情况

- **所有 150 条都有 judge criteria**
- **criteria 数量分布**: min=1, max=14, avg=11.6
- **unique criteria 总数**: 37
- **tier 分布**: basic=1,018 次, advanced=727 次

## 10. 章节/集数编号分布

**小说章节** (80 条): 范围 1-53, 平均 13, 中位数 10
**原创剧本** (54 条): 范围 2-68, 平均 39, 中位数 42
**改编剧本** (11 条): 范围 1-5, 平均 3, 中位数 3

## 11. 设计版本分布

| 设计版本 | 条数 | 占比 |
|---------|------|------|
| dsv2 | 64 | 42.7% |
| dsv3 | 56 | 37.3% |
| dsv1 | 16 | 10.7% |
| nts_v3 | 14 | 9.3% |
