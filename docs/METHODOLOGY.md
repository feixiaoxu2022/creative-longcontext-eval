# 长上下文评测方法论

## 背景

传统的长上下文 benchmark（如 LongBench、RULER）多基于人工构造的合成任务（如 needle-in-haystack、长文档问答），这些任务与真实 Agent 应用场景存在较大差距：

1. **任务真实性不足** - 合成任务往往只需"定位+提取"能力，而真实创作任务需要理解全文、保持一致性、生成高质量内容
2. **评判标准单一** - 多采用精确匹配或 F1，无法衡量创作质量的多维度要求
3. **缺乏长期依赖验证** - 难以测试模型是否真正理解了数万 token 的前文，还是只依赖局部信息

本框架从**真实 Agent 执行轨迹**中提取评测数据，解决上述问题。

## 核心设计

### 1. 数据来源：真实场景轨迹

从三个创意类 Agent 场景（NWA/SD/NTS）中选取高质量执行样本：
- **NWA (小说写作)**：Agent 已写完前 22 章（4万 tokens），现在续写第 23 章
- **SD (短剧编写)**：Agent 已写完前 13 集剧本（5万 tokens），现在写第 14 集
- **NTS (小说改编)**：Agent 基于 1万字原著小说改编第 3 集剧本

这些任务的输入自然包含**长上下文**（已有创作成果 + 参考设定），且输出质量可通过**LLM Judge**评估。

### 2. 双模式设计

#### Instruct 模式
- **输入**：系统设定 + 用户需求 + 参考文档 + 已有成果 + 当前任务指令
- **能力要求**：理解指令、遵循业务规则、参考前文保持一致性
- **适用模型**：所有 instruct 模型（Claude、GPT、国产模型等）

#### Pretrain 模式
- **输入**：已有创作成果（纯文本，无指令）
- **能力要求**：从已有文本自然续写，保持风格和逻辑连贯
- **适用模型**：Base 模型、未对齐模型

**为什么需要 Pretrain 模式？**
- 部分模型（如 EB5-midtrain）没有指令遵循能力，但长上下文建模能力强
- 避免"指令遵循能力"混淆"长上下文理解能力"的评估

### 3. 长度分布设计

| 长度段 | Token 范围 | Instruct 样本数 | Pretrain 样本数 |
|--------|------------|-----------------|-----------------|
| <10K   | 0 - 10,000 | 28 | 78 |
| 10K-20K | 10,001 - 20,000 | 25 | 62 |
| 20K-40K | 20,001 - 40,000 | 30 | 63 |
| 40K-70K | 40,001 - 70,000 | 40 | 70 |
| 70K-100K | 70,001 - 100,000 | 27 | 27 |

**设计原则**：
- 均衡覆盖各长度段，避免某段过少导致统计不可靠
- 40K-70K 段样本数最多（真实场景中最常见的长度）
- 70K-100K 段用于测试模型极限

### 4. 评判标准：LLM Judge

每个样本有 3-12 个 `judge_criteria`，分为三层：

#### Gate 层（门槛项）
- **定义**：任何一项不通过，整体质量判定为"不合格"
- **示例**：格式正确、无乱码、基本逻辑通顺
- **目的**：过滤严重错误（如生成空白、返回乱码、完全偏离任务）

#### Basic 层（基础质量）
- **定义**：影响 content_score 计算，权重较高
- **示例**：角色行为符合人设、台词信息密度合理、剧情衔接自然
- **目的**：衡量模型是否理解前文并生成符合要求的内容

#### Advanced 层（高级质量）
- **定义**：影响 content_score 计算，权重较低
- **示例**：镜头语言丰富、情感张力强、创意亮点突出
- **目的**：区分优秀模型与普通模型

**评分公式**：
```python
if any(gate_check fails):
    quality_level = "unqualified"
    overall_score = 0
else:
    content_score = weighted_avg(basic + advanced checks)
    if content_score >= 75:
        quality_level = "good"
    elif content_score >= 60:
        quality_level = "qualified"
    else:
        quality_level = "unqualified"
```

### 5. Reference Output 的使用

每个样本的 `reference_output` 是原场景中**高质量模型（如 Claude Opus）的实际输出**，已通过场景的完整 checker 验证。

LLM Judge 通过对比待测模型输出和 reference_output，评估：
- **是否保持了前文一致性**（如角色性格、已发生的剧情）
- **是否达到了基本质量要求**（如信息密度、逻辑连贯）
- **是否符合业务规则**（如短剧集数约束、镜头语言标注）

**注意**：reference_output 不是"标准答案"，而是"质量基准"。Judge 不要求完全一致，而是评估相对质量。

## 评测流程

```
1. 数据准备
   └─ 从场景 repo 收集 evaluation_outputs/
   └─ 运行 build_singleturn_dataset.py 构建数据集

2. 模型推理
   └─ 调用模型 API，输入 input，获取输出
   └─ 记录 inference_success、error、finish_reason

3. LLM Judge 评判
   └─ 对每个 judge_criteria，调用 Judge 模型对比输出与 reference
   └─ 返回 pass/fail + reason

4. 结果分析
   └─ 按长度段统计推理成功率、平均分数
   └─ 识别模型在哪个长度段开始衰减
   └─ 对比不同模型的长上下文能力
```

## 关键指标

### 推理成功率
- **定义**：`inference_success == true` 的样本比例
- **意义**：模型是否能稳定处理该长度的输入（未超过 token 限制、未超时）

### Gate 通过率
- **定义**：所有 gate 层检查项均通过的样本比例
- **意义**：模型生成的基本可用性（无严重错误）

### Content Score
- **定义**：basic + advanced 层检查项的加权平均分
- **意义**：内容质量的综合评分（60-75 合格，75+ 优秀）

### 长度衰减曲线
- **X 轴**：长度段（<10K, 10K-20K, ..., 70K-100K）
- **Y 轴**：推理成功率 / Gate 通过率 / Content Score
- **意义**：模型在哪个长度开始出现性能下降

## 与其他 Benchmark 的对比

| Benchmark | 任务来源 | 评判方式 | 长度范围 | 真实度 |
|-----------|----------|----------|----------|--------|
| **LongBench** | 合成任务 | 精确匹配/F1 | 4K-40K | 低 |
| **RULER** | 合成任务 | 精确匹配 | 4K-128K | 低 |
| **Infinity-Bench** | 合成任务 | 精确匹配 | 100K-1M | 低 |
| **本框架** | 真实 Agent 轨迹 | LLM Judge（多维度） | 10K-100K | **高** |

## 未来扩展

1. **新增场景** - 加入更多创意类场景（如知识视频创作、营销文案）
2. **更长长度** - 扩展到 100K-200K（需要支持更长上下文的模型）
3. **更多模态** - 加入图文混合、多模态创作任务
4. **动态难度** - 根据模型能力自适应调整任务难度

## 参考文献

- [LongBench: A Bilingual, Multitask Benchmark for Long Context Understanding](https://arxiv.org/abs/2308.14508)
- [RULER: What's the Real Context Size of Your Long-Context Language Models?](https://arxiv.org/abs/2404.06654)
- [Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172)
