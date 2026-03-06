# 代码分析结论

## 结论 1：`estimate_tokens()` 高估 token 数，导致 length_bin 分布整体偏移

**涉及文件**：`build_singleturn_dataset.py:703-716`

### 背景

数据集构建阶段（`build_singleturn_dataset.py`）使用以下公式估算 input token 数：

```python
def estimate_tokens(text):
    chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    chinese_ratio = chinese_chars / len(text)
    avg_chars_per_token = 1.5 * chinese_ratio + 4 * (1 - chinese_ratio)
    return int(len(text) / avg_chars_per_token)
```

中文部分采用 **1.5 chars/token** 的假设。

### 问题

现代中文 tokenizer（GLM、Qwen 等）对汉字的编码效率更高，实际比例更接近 **1.0 chars/token**（即 1 个汉字对应 1 个 token）。因此对中文为主的文本，`estimate_tokens()` 会**系统性地高估约 1.5 倍**。

### 影响链路

估算值直接决定每条数据落入哪个 `length_bin`，而 `length_bin` 是分层采样的依据（`build_singleturn_dataset.py:975-980`）：

```
LENGTH_BIN_TARGETS = {
    "10K-20K":  88,
    "20K-40K":  99,
    "40K-70K": 110,
    "70K-100K": 33,
}
```

高估的结果是：一条实际 token 数落在较短 bin 的数据，会被分配到更长的 bin 里参与采样。最终产出的 330 条数据，**实际 token 长度比 `length_bin` 标签显示的要短**，长度分布整体虚标偏高。

### 不影响的方面

- **不会触发 `<10K` 的丢弃门槛**：高估只会让数据往更长的 bin 偏，而不是更短，所以不会有原本合格的数据因为被估短而被丢弃。
- **不会导致推理失败（OOM/超时）**：送进模型的实际 prompt 比预期更短，模型压力只会更小。

### 备注

pretrain 版本（`convert_to_pretrain.py:359`）用更粗糙的 `len(text) // 3`，但 pretrain 的 `input` 字段已被替换为剥离 prompt 框架后的纯正文，token 数量级不同，该估算仅用于统计分布，不参与筛选，无实质影响。
