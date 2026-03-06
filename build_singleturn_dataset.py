#!/usr/bin/env python3
"""
Agent 评测轨迹 → 单轮长上下文评测数据集 Pipeline

将三个创意写作场景（NWA/NTS/SD）的多轮 Agent 评测轨迹转化为
单轮长上下文评测数据，每条数据自包含所有上下文。

用法：
    python3 scripts/build_singleturn_dataset.py \
        --scenarios nwa,nts,sd \
        --output singleturn_dataset.jsonl \
        --target-count 150 \
        [--dry-run]
"""

import argparse
import json
import os
import re
import random
import sys
from collections import defaultdict
from pathlib import Path


# ── 场景配置 ──────────────────────────────────────────────────────

SCENARIO_CONFIGS = {
    "nwa": {
        "base_dir": "tmp_scenarios/novel_writing_alchemist",
        "eval_patterns": ["eval_dsv1_*", "eval_dsv2_*"],
        "judge_criteria_dir": "check_definitions/check_revisions/rev_009/judge_criteria",
    },
    "nts": {
        "base_dir": "tmp_scenarios/novel_to_script",
        "eval_patterns": ["eval_nts_v3_*"],
        "judge_criteria_dir": "check_definitions/judge_criteria",
    },
    "sd": {
        "base_dir": "tmp_scenarios/shortdrama",
        "eval_patterns": ["eval_dsv3_*"],
        "judge_criteria_dir": "check_definitions/check_revisions/rev_006/judge_criteria",
    },
}

# 单轮版 system prompt（按 scenario + design_version 索引）
# 文件位于 singleturn_longcontext_eval/system_prompts/
SINGLETURN_SYSTEM_PROMPTS = {}


def load_singleturn_system_prompts(project_root):
    """加载单轮版 system prompt 文件"""
    prompts_dir = os.path.join(project_root, "singleturn_longcontext_eval", "system_prompts")
    mapping = {
        ("nwa", "dsv1"): "nwa_dsv1.md",
        ("nwa", "dsv2"): "nwa_dsv2.md",
        ("nts", "nts_v3"): "nts.md",
        ("sd", "dsv3"): "sd.md",
    }
    for key, filename in mapping.items():
        filepath = os.path.join(prompts_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                SINGLETURN_SYSTEM_PROMPTS[key] = f.read().strip()
        else:
            print(f"警告: 缺少单轮 system prompt: {filepath}", file=sys.stderr)


def get_singleturn_system_prompt(scenario, design_version):
    """获取单轮版 system prompt"""
    key = (scenario, design_version)
    if key in SINGLETURN_SYSTEM_PROMPTS:
        return SINGLETURN_SYSTEM_PROMPTS[key]
    # fallback: 尝试不带版本的
    for k, v in SINGLETURN_SYSTEM_PROMPTS.items():
        if k[0] == scenario:
            return v
    return ""


HIGH_QUALITY_MODELS = {
    "claude-opus-4-5-20251101",
    "claude-opus-4-6",
    "gemini-3-pro-preview",
    "gemini-3.1-pro-preview",
}

# 跳过的文件（非创作产出）
SKIP_PATTERNS = [
    r"^writing_log\.md$",
    r"^merge_.*\.py$",
    r"^build_.*\.py$",
    r"^gen_.*\.py$",
    r".*\.sh$",
    r"^temp_act_.*\.json$",
    r"^outline_act_.*\.json$",
    r"^outline_part\d+\.json$",
    r"^tmp_ep_.*\.json$",
]

# ── 阶段分类 ──────────────────────────────────────────────────────

def classify_stage(scenario, path):
    """根据写入文件路径判断创作阶段"""
    basename = os.path.basename(path)

    if scenario == "nwa":
        if basename == "creative_intent.json":
            return "recipe"
        if basename == "characters.json":
            return "character"
        if basename == "outline.json":
            return "outline"
        if re.match(r"chapters/chapter_\d+\.md", path):
            return "chapter_writing"
        return None

    elif scenario == "nts":
        if basename == "novel_analysis.json":
            return "analysis"
        if basename == "drama_plan.json":
            return "planning"
        if re.match(r"scripts/episode_\d+\.json", path):
            return "script_writing"
        return None

    elif scenario == "sd":
        if basename == "topic_brief.json":
            return "topic_brief"
        if basename == "characters.json":
            return "character"
        if basename == "outline.json":
            return "outline"
        if re.match(r"_part\d+\.json$", basename):
            return "outline"
        if re.match(r"scripts/episode_\d+_script\.json", path):
            return "script_writing"
        return None

    return None


def is_skip_file(path):
    """判断是否应跳过此文件"""
    basename = os.path.basename(path)
    for pattern in SKIP_PATTERNS:
        if re.match(pattern, basename):
            return True
    return False


def classify_output_type(scenario, stage, write_path):
    """分类产出物类型（人类可读的中文标签）"""
    type_map = {
        ("nwa", "recipe"): "创作配方",
        ("nwa", "character"): "角色设定",
        ("nwa", "outline"): "故事大纲",
        ("nwa", "chapter_writing"): "小说章节",
        ("nts", "analysis"): "拆书分析",
        ("nts", "planning"): "改编策划",
        ("nts", "script_writing"): "改编剧本",
        ("sd", "topic_brief"): "选题简报",
        ("sd", "character"): "角色卡",
        ("sd", "outline"): "分集大纲",
        ("sd", "script_writing"): "原创剧本",
    }
    return type_map.get((scenario, stage), f"{scenario}/{stage}")


def extract_sequence_number(write_path):
    """从文件路径提取章节/集数编号，无则返回 None"""
    basename = os.path.basename(write_path)
    # chapters/chapter_07.md → 7
    m = re.search(r"chapter_(\d+)", basename)
    if m:
        return int(m.group(1))
    # scripts/episode_5.json 或 scripts/episode_5_script.json → 5
    m = re.search(r"episode_(\d+)", basename)
    if m:
        return int(m.group(1))
    # _part3.json → 3
    m = re.search(r"_part(\d+)", basename)
    if m:
        return int(m.group(1))
    return None


def extract_genre(scenario, data_id):
    """从 sample_id 中提取题材/类型标签"""
    if scenario == "nwa":
        # NW_CLEAR_MEDIUM_ADVENTURE_001 → adventure
        # NW_IP_MEDIUM_NEUTRAL_001 → neutral (IP改编)
        # NW_ULTRA_SHORT_ANGSTY_001 → angsty
        # NW_VAGUE_MEDIUM_SWEET_DRAMA_001 → sweet_drama
        parts = data_id.upper().replace("NW_", "").split("_")
        # 格式: {CLARITY}_{LENGTH}_{GENRE...}_{NUM}
        # 跳过 clarity 和 length tier，提取 genre
        if len(parts) >= 3:
            # 去掉第一个(clarity)和第二个(length)和最后一个(编号)
            genre_parts = parts[2:-1]
            return "_".join(genre_parts).lower()
        return "unknown"

    elif scenario == "nts":
        # NTS_HISTORICAL_MEDIUM_3EP_FLEX_DOUYIN_001 → historical
        # NTS_SCHOOL_SWEET_SHORT_3EP_FLEX_DOUYIN_001 → school_sweet
        parts = data_id.upper().replace("NTS_", "").split("_")
        # 找到 SHORT/MEDIUM/LONG 的位置，之前的都是 genre
        genre_parts = []
        for p in parts:
            if p in ("SHORT", "MEDIUM", "LONG"):
                break
            genre_parts.append(p)
        return "_".join(genre_parts).lower() if genre_parts else "unknown"

    elif scenario == "sd":
        # SD_A_ancient_court_30 → ancient_court
        # SD_B_underdog_comeback_60 → underdog_comeback
        # SD_C_mystery_thriller_70_theme_h2629 → mystery_thriller
        # SD_E_son_in_law_70 → son_in_law
        parts = data_id.split("_")
        if len(parts) >= 4:
            # 跳过 SD 和 difficulty letter，提取到数字（集数）之前的部分
            genre_parts = []
            for p in parts[2:]:
                if re.match(r"^\d+$", p):
                    break
                genre_parts.append(p)
            return "_".join(genre_parts).lower() if genre_parts else "unknown"
        return "unknown"

    return "unknown"


# ── 轨迹解析 ──────────────────────────────────────────────────────

def parse_tool_args(arguments):
    """解析 tool_call 的 arguments（可能是 str 或 dict）"""
    if isinstance(arguments, dict):
        return arguments
    if isinstance(arguments, str):
        try:
            return json.loads(arguments)
        except (json.JSONDecodeError, TypeError):
            return {}
    return {}


def parse_tool_result(result):
    """解析 tool_call 的 result，提取实际返回内容"""
    if isinstance(result, dict):
        return result
    if isinstance(result, str):
        try:
            parsed = json.loads(result)
            # 处理嵌套 {"content": [{"type": "text", "text": "..."}]} 格式
            if "content" in parsed and isinstance(parsed["content"], list):
                for item in parsed["content"]:
                    if isinstance(item, dict) and item.get("type") == "text":
                        try:
                            return json.loads(item["text"])
                        except (json.JSONDecodeError, TypeError):
                            return {"text": item["text"]}
            return parsed
        except (json.JSONDecodeError, TypeError):
            return {"raw": result}
    return {}


def extract_write_path(tool_call):
    """从 write_file 调用中提取写入路径"""
    args = parse_tool_args(tool_call.get("arguments", ""))
    return args.get("path", "")


def extract_write_content(tool_call):
    """从 write_file 调用中提取写入内容"""
    args = parse_tool_args(tool_call.get("arguments", ""))
    return args.get("content", "")


def extract_read_content(tool_call):
    """从 read_file 调用的 result 中提取文件内容"""
    result = parse_tool_result(tool_call.get("result", ""))
    return result.get("content", "")


def extract_read_path(tool_call):
    """从 read_file 调用中提取读取路径"""
    args = parse_tool_args(tool_call.get("arguments", ""))
    return args.get("path", "")


# ── 上下文收集 ────────────────────────────────────────────────────

def collect_prior_workspace_files(tool_calls, write_index):
    """收集当前 write 之前所有 write_file 写入的文件（按最终版本）

    返回 dict: {path: content}，对于同一路径多次写入只保留最后一次。
    """
    files = {}
    for i in range(write_index):
        tc = tool_calls[i]
        if tc.get("name") == "write_file":
            path = extract_write_path(tc)
            content = extract_write_content(tc)
            if path and content and not is_skip_file(path):
                files[path] = content
    return files


def collect_env_knowledge_files(env_dir):
    """收集 _env/data_pools/skills/ 下的环境知识文档"""
    skills_dir = os.path.join(env_dir, "data_pools", "skills")
    files = {}
    if os.path.isdir(skills_dir):
        for fname in sorted(os.listdir(skills_dir)):
            fpath = os.path.join(skills_dir, fname)
            if os.path.isfile(fpath) and fname.endswith(".md"):
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        files[fname] = f.read()
                except Exception:
                    pass
    return files


def read_workspace_file(env_dir, rel_path):
    """从 workspace 目录读取最终版文件"""
    fpath = os.path.join(env_dir, "workspace", rel_path)
    if os.path.isfile(fpath):
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return ""
    return ""


# ── 输入组装 ──────────────────────────────────────────────────────

def get_stage_description(scenario, stage, write_path):
    """为当前写入生成任务描述（单轮模式，不含文件路径）"""
    basename = os.path.basename(write_path)

    if scenario == "nwa":
        descs = {
            "recipe": "创作配方，包含用户需求分析、X-Y轴配方选择、化学反应设计",
            "character": "角色设定，包含角色基本信息、性格特征、关系网络",
            "outline": "故事大纲，包含分幕分章结构、情节走向、转折点设计",
        }
        if stage == "chapter_writing":
            m = re.search(r"chapter_(\d+)", basename)
            ch_num = m.group(1) if m else "?"
            return f"第{ch_num}章正文，要求按照大纲设计推进情节，保持人物性格一致，语言风格符合题材"
        return descs.get(stage, "创作内容")

    elif scenario == "nts":
        descs = {
            "analysis": "拆书分析报告，分析原著核心冲突、名场面、人物关系",
            "planning": "改编策划文档，规划分集结构、核心保留/删减决策",
        }
        if stage == "script_writing":
            m = re.search(r"episode_(\d+)", basename)
            ep_num = m.group(1) if m else "?"
            return f"第{ep_num}集剧本，包含场景描述、角色对话、镜头语言"
        return descs.get(stage, "创作内容")

    elif scenario == "sd":
        descs = {
            "topic_brief": "选题简报，包含核心设定、钩子设计、目标受众分析",
            "character": "角色卡，包含角色设定、关系网络、视觉描述",
            "outline": "分集大纲，包含每集核心事件、转折点、情绪节奏",
        }
        if stage == "script_writing":
            m = re.search(r"episode_(\d+)", basename)
            ep_num = m.group(1) if m else "?"
            return f"第{ep_num}集剧本，包含场景描述、角色对话、镜头指示"
        return descs.get(stage, "创作内容")

    return "创作内容"


def select_env_files_for_stage(scenario, stage, env_files):
    """根据阶段选择性包含环境文档（避免无关文档膨胀输入）"""
    if not env_files:
        return {}

    if scenario == "nwa":
        stage_skills = {
            "recipe": ["RECIPE_KNOWLEDGE.md"],
            "character": ["CHARACTER_DESIGN_GUIDE.md", "CHARACTER_NAMING_GUIDE.md"],
            "outline": ["OUTLINE_DESIGN_GUIDE.md"],
            "chapter_writing": ["WRITING_TECHNIQUE_GUIDE.md", "CONSISTENCY_MANAGEMENT_GUIDE.md"],
        }
        wanted = stage_skills.get(stage, [])
        if wanted:
            return {k: v for k, v in env_files.items() if k in wanted}
        return env_files

    # NTS 和 SD 的 skills 文件较少，全部包含
    return env_files


def clean_skill_content(content):
    """清理 skill 参考文档中的 Agent 环境残留引用"""
    # 删除包含 Agent 工具/文件引用的整行
    lines = content.split("\n")
    cleaned = []
    for line in lines:
        stripped = line.strip()
        # 删除提到工具调用的行
        if "request_human_review" in stripped and ("调用" in stripped or "通过" in stripped):
            continue
        # 删除提到 output_specifications 的行
        if "output_specifications" in stripped:
            continue
        # 删除提到 workspace/ 目录的行
        if "workspace/" in stripped and ("写入" in stripped or "创建" in stripped or "目录" in stripped):
            continue
        cleaned.append(line)
    return "\n".join(cleaned)


def assemble_input(system_prompt, user_query, env_files, prior_files,
                   stage, write_path, scenario, source_novel_content=None):
    """组装单轮输入文本（使用预制的单轮版 system prompt）"""
    parts = []

    # 1. System prompt（已经是单轮版，不含工具/文件系统指令）
    parts.append("# 系统设定\n")
    parts.append(system_prompt.strip())
    parts.append("\n")

    # 2. 用户需求
    parts.append("\n# 用户需求\n")
    parts.append(user_query.strip())
    parts.append("\n")

    # 3. 参考文档（skills）— 清理其中的 Agent 环境残留
    if env_files:
        parts.append("\n# 参考文档\n")
        for fname, content in sorted(env_files.items()):
            parts.append(f"\n## {fname}\n")
            cleaned = clean_skill_content(content)
            parts.append(cleaned.strip())
            parts.append("\n")

    # 4. NTS 特有：原著小说
    if source_novel_content and scenario == "nts":
        parts.append("\n# 原著小说\n")
        parts.append(source_novel_content.strip())
        parts.append("\n")

    # 5. 已有创作成果
    if prior_files:
        parts.append("\n# 已有创作成果\n")

        # 按文件类型分组排序
        categorized = categorize_prior_files(scenario, prior_files)
        for category_name, files in categorized:
            if files:
                parts.append(f"\n## {category_name}\n")
                for fpath, content in files:
                    # 清理路径前缀（workspace/ 等）
                    display_path = re.sub(r"^workspace/", "", fpath)
                    parts.append(f"\n### {display_path}\n")
                    parts.append(content.strip())
                    parts.append("\n")

    # 6. 当前任务
    task_desc = get_stage_description(scenario, stage, write_path)
    parts.append(f"\n# 当前任务\n")
    parts.append(f"请撰写：{task_desc}\n")

    return "\n".join(parts)


def categorize_prior_files(scenario, prior_files):
    """将已有文件按类别分组，便于组织输入"""
    categories = []

    if scenario == "nwa":
        recipe = [(p, c) for p, c in prior_files.items() if "creative_intent" in p]
        chars = [(p, c) for p, c in prior_files.items() if "characters" in p]
        outline = [(p, c) for p, c in prior_files.items() if "outline" in p and "act" not in p and "part" not in p]
        chapters = sorted(
            [(p, c) for p, c in prior_files.items() if p.startswith("chapters/")],
            key=lambda x: x[0]
        )
        if recipe:
            categories.append(("创作配方", recipe))
        if chars:
            categories.append(("角色设定", chars))
        if outline:
            categories.append(("故事大纲", outline))
        if chapters:
            categories.append(("已完成章节", chapters))

    elif scenario == "nts":
        analysis = [(p, c) for p, c in prior_files.items() if "novel_analysis" in p]
        plan = [(p, c) for p, c in prior_files.items() if "drama_plan" in p]
        scripts = sorted(
            [(p, c) for p, c in prior_files.items() if p.startswith("scripts/")],
            key=lambda x: x[0]
        )
        if analysis:
            categories.append(("拆书分析", analysis))
        if plan:
            categories.append(("改编策划", plan))
        if scripts:
            categories.append(("已完成剧本", scripts))

    elif scenario == "sd":
        brief = [(p, c) for p, c in prior_files.items() if "topic_brief" in p]
        chars = [(p, c) for p, c in prior_files.items() if "characters" in p]
        outlines = sorted(
            [(p, c) for p, c in prior_files.items()
             if "outline" in p or re.match(r"_part\d+\.json$", os.path.basename(p))],
            key=lambda x: x[0]
        )
        scripts = sorted(
            [(p, c) for p, c in prior_files.items() if p.startswith("scripts/")],
            key=lambda x: x[0]
        )
        if brief:
            categories.append(("选题简报", brief))
        if chars:
            categories.append(("角色卡", chars))
        if outlines:
            categories.append(("分集大纲", outlines))
        if scripts:
            categories.append(("已完成剧本", scripts))

    return categories


# ── Judge Criteria 匹配 ──────────────────────────────────────────

def load_judge_criteria(scenario_dir, criteria_rel_dir):
    """加载 judge_criteria YAML 文件，解析为 {section_name: criteria_text}"""
    import re

    def clean_and_fix_criteria_text(text):
        """清理 YAML 格式并调整标题层级

        1. 去掉 'llm_judge_criteria: |' 头部
        2. 去掉每行开头的缩进（通常是2个空格）
        3. 调整标题层级：# -> ###, ## -> ####
        """
        # 去掉 YAML 头
        text = re.sub(r'^llm_judge_criteria:\s*\|\s*\n?', '', text, flags=re.MULTILINE)

        # 去掉每行开头的缩进
        lines = []
        for line in text.split('\n'):
            if line.startswith('  '):
                line = line[2:]
            lines.append(line)
        text = '\n'.join(lines)

        # 调整标题层级
        lines = []
        for line in text.split('\n'):
            # 匹配标题行（以 # 开头）
            if re.match(r'^(#{1,6})\s+', line):
                # 给每个标题增加两个 #
                line = '##' + line
            lines.append(line)

        return '\n'.join(lines).strip()

    criteria_dir = os.path.join(scenario_dir, criteria_rel_dir)
    all_criteria = {}

    if not os.path.isdir(criteria_dir):
        return all_criteria

    for fname in sorted(os.listdir(criteria_dir)):
        if not fname.endswith(".yaml"):
            continue
        fpath = os.path.join(criteria_dir, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            continue

        # 简单解析：按 "## section_name" 切分
        current_section = None
        current_lines = []
        for line in content.split("\n"):
            if line.startswith("## "):
                if current_section and current_lines:
                    # 清理 YAML 格式并修复标题层级
                    criteria_text = "\n".join(current_lines)
                    all_criteria[current_section] = clean_and_fix_criteria_text(criteria_text)
                current_section = line[3:].strip()
                current_lines = []
            elif current_section is not None:
                current_lines.append(line)

        if current_section and current_lines:
            # 清理 YAML 格式并修复标题层级
            criteria_text = "\n".join(current_lines)
            all_criteria[current_section] = clean_and_fix_criteria_text(criteria_text)

    return all_criteria


# 每个场景每个阶段应匹配的 criteria section 名
STAGE_CRITERIA_MAP = {
    "nwa": {
        "chapter_writing": {
            "basic": [
                "主题一致性", "主要角色一致性", "人物设定一致性",
                "逻辑硬伤", "语言纯净性", "情节推进", "完整叙事文本",
                "叙事调性匹配", "后期章节跑偏",
            ],
            "advanced": [
                "角色语言辨识度", "叙事密度与手法", "剧情节奏合理性",
                "钩子设计", "情感弧线层次",
            ],
        },
        "outline": {
            "basic": ["outline结构完整性"],
            "advanced": ["outline叙事张力"],
        },
        "character": {
            "basic": ["角色关系设计张力", "角色动机设计深度"],
            "advanced": ["角色成长弧线设计"],
        },
    },
    "nts": {
        "script_writing": {
            "basic": [
                "选材能力基础标准", "视觉化能力基础标准", "节奏把控基础标准",
                "改编连贯性综合标准", "台词口语化标准", "角色外貌描述完整性",
                "内容充实度标准",
            ],
            "advanced": [
                "视觉化能力优秀标准", "节奏把控优秀标准", "氛围营造能力",
                "台词深度与角色辨识度标准", "转场设计质量标准",
            ],
        },
        "analysis": {
            "basic": ["拆书分析内容质量标准"],
        },
    },
    "sd": {
        "script_writing": {
            # SD 的检查项名称直接使用 YAML section 名称
            "basic": [
                "角色人设鲜明度",
                "节奏控制基础检查",
                "台词信息过载检测",
                "台词断句与长度控制",
                "台词书面腔检测",
                "小说式独白/旁白混入dialogue检测",
                "无注水/拖沓段落",
            ],
            "advanced": [
                "氛围营造能力",
            ],
        },
        "outline": {
            "basic": ["钩子吸引力基础检查"],
            "advanced": ["钩子吸引力优秀检查"],
        },
        "topic_brief": {
            "basic": ["剧本核心设定吸引力"],
        },
    },
}


def match_criteria(scenario, stage, all_criteria):
    """为特定场景/阶段匹配 judge criteria"""
    mapping = STAGE_CRITERIA_MAP.get(scenario, {}).get(stage, {})
    matched = []

    for tier, section_names in mapping.items():
        for name in section_names:
            if name in all_criteria:
                matched.append({
                    "name": name,  # YAML section 名称(作为唯一标识)
                    "check_name": name,  # 兼容性:export_readable.py 会读这个字段
                    "tier": tier,
                    "criteria_text": all_criteria[name],
                })

    return matched


# ── 长度分桶 ──────────────────────────────────────────────────────

def estimate_tokens(text):
    """粗略估算 token 数（中文约 1.5 char/token，英文约 4 char/token）
    对中文为主的文本用 len/2 作为近似"""
    if not text:
        return 0
    # 统计中文字符比例来调整
    chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    total_chars = len(text)
    if total_chars == 0:
        return 0
    chinese_ratio = chinese_chars / total_chars
    # 中文 ~1.5 chars/token, 英文 ~4 chars/token
    avg_chars_per_token = 1.5 * chinese_ratio + 4 * (1 - chinese_ratio)
    return int(total_chars / avg_chars_per_token)


def get_length_bin(tokens):
    """将 token 数分入长度区间，< 10K 归入 'under_10K' 会被过滤"""
    if tokens < 10000:
        return "under_10K"
    elif tokens < 20000:
        return "10K-20K"
    elif tokens < 40000:
        return "20K-40K"
    elif tokens < 70000:
        return "40K-70K"
    else:
        return "70K-100K"


# ── 主逻辑 ────────────────────────────────────────────────────────

def find_eval_dirs(base_dir, patterns):
    """查找评测输出目录"""
    eval_output_dir = os.path.join(base_dir, "evaluation_outputs")
    if not os.path.isdir(eval_output_dir):
        return []

    dirs = []
    for entry in sorted(os.listdir(eval_output_dir)):
        entry_path = os.path.join(eval_output_dir, entry)
        if not os.path.isdir(entry_path):
            continue
        for pattern in patterns:
            # 简单 glob 匹配
            pat_re = pattern.replace("*", ".*")
            if re.match(pat_re, entry):
                dirs.append(entry_path)
                break
    return dirs


def extract_model_name(eval_dir_name):
    """从 eval 目录名中提取模型名"""
    # eval_dsv2_20260211_122519_claude-opus-4-5-20251101
    # eval_nts_v3_20260219_212800_claude-opus-4-6
    parts = os.path.basename(eval_dir_name).split("_")
    # 找到日期时间戳之后的部分（格式 YYYYMMDD_HHMMSS）
    for i, p in enumerate(parts):
        if re.match(r"^\d{8}$", p) and i + 1 < len(parts) and re.match(r"^\d{6}$", parts[i + 1]):
            return "_".join(parts[i + 2:])
    return "_".join(parts[-2:])


def extract_design_version(eval_dir_name):
    """提取设计版本（dsv1/dsv2/nts_v3/dsv3）"""
    basename = os.path.basename(eval_dir_name)
    if "dsv1" in basename:
        return "dsv1"
    elif "dsv2" in basename:
        return "dsv2"
    elif "nts_v3" in basename or "nts_v3" in basename:
        return "nts_v3"
    elif "dsv3" in basename:
        return "dsv3"
    return "unknown"


def build_candidate(scenario, sample_path, env_dir, all_criteria, tool_calls,
                    write_index, system_prompt, user_query, data_id, model_name,
                    design_version):
    """为一个 write_file 调用构建候选数据"""
    write_call = tool_calls[write_index]
    write_path = extract_write_path(write_call)
    write_content = extract_write_content(write_call)

    if not write_path or not write_content:
        return None

    # 跳过非创作产出
    if is_skip_file(write_path):
        return None

    # 判断创作阶段
    stage = classify_stage(scenario, write_path)
    if stage is None:
        return None

    # 对于同一路径的多次写入，只取最后一次
    # 检查后续是否还有同路径的写入
    for j in range(write_index + 1, len(tool_calls)):
        if tool_calls[j].get("name") == "write_file":
            later_path = extract_write_path(tool_calls[j])
            if later_path == write_path:
                return None  # 后续有覆盖，跳过此次

    # 收集上下文
    prior_files = collect_prior_workspace_files(tool_calls, write_index)
    env_files = collect_env_knowledge_files(env_dir)
    selected_env_files = select_env_files_for_stage(scenario, stage, env_files)

    # NTS 特有：原著小说内容
    source_novel = None
    if scenario == "nts":
        source_novel = read_workspace_file(env_dir, "source_novel.md")

    # 组装 input（使用单轮版 system prompt）
    singleturn_sp = get_singleturn_system_prompt(scenario, design_version)
    input_text = assemble_input(
        system_prompt=singleturn_sp,
        user_query=user_query,
        env_files=selected_env_files,
        prior_files=prior_files,
        stage=stage,
        write_path=write_path,
        scenario=scenario,
        source_novel_content=source_novel,
    )

    # 获取 reference_output
    reference = read_workspace_file(env_dir, write_path)
    if not reference:
        # fallback：使用 write_file 调用的 content
        reference = write_content

    # 匹配 judge criteria
    criteria = match_criteria(scenario, stage, all_criteria)

    # 估算 token 数
    input_tokens = estimate_tokens(input_text)

    # 判断长度分桶
    length_bin = get_length_bin(input_tokens)

    # 判断来源质量
    source_quality = "high" if model_name in HIGH_QUALITY_MODELS else "mixed"

    # 估算 reference_output token 数
    ref_tokens = estimate_tokens(reference)

    # 提取产出物类型
    output_type = classify_output_type(scenario, stage, write_path)

    # 提取章节/集数编号
    seq_num = extract_sequence_number(write_path)

    # 提取题材（从 sample_id）
    genre = extract_genre(scenario, data_id)

    # 构建 ID
    stage_suffix = os.path.splitext(os.path.basename(write_path))[0]
    candidate_id = f"{scenario}_{design_version}_{model_name}_{data_id}_{stage_suffix}"

    return {
        "id": candidate_id,
        "scenario": scenario,
        "design_version": design_version,
        "source_model": model_name,
        "source_sample_id": data_id,
        "stage": stage,
        "output_file": write_path,
        "output_type": output_type,
        "genre": genre,
        "sequence_num": seq_num,
        "input_tokens_est": input_tokens,
        "reference_output_tokens_est": ref_tokens,
        "length_bin": length_bin,
        "source_quality": source_quality,
        "has_judge_criteria": len(criteria) > 0,
        "judge_criteria_count": len(criteria),
        "system_prompt": singleturn_sp,
        "input": input_text,
        "reference_output": reference,
        "judge_criteria": criteria,
    }


def extract_candidates_from_sample(scenario, sample_path, env_dir, all_criteria):
    """从一个样本文件中提取所有候选数据"""
    try:
        with open(sample_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"  [WARN] 无法读取 {sample_path}: {e}", file=sys.stderr)
        return []

    if data.get("execution_status") != "success":
        return []

    tool_calls = data.get("tool_call_list", [])
    system_prompt = data.get("system", "")
    user_query = data.get("query", "")
    data_id = data.get("data_id", "")
    model_name = data.get("model", "")
    eval_dir = os.path.dirname(sample_path)
    design_version = extract_design_version(eval_dir)

    candidates = []
    for i, tc in enumerate(tool_calls):
        if tc.get("name") == "write_file":
            candidate = build_candidate(
                scenario=scenario,
                sample_path=sample_path,
                env_dir=env_dir,
                all_criteria=all_criteria,
                tool_calls=tool_calls,
                write_index=i,
                system_prompt=system_prompt,
                user_query=user_query,
                data_id=data_id,
                model_name=model_name,
                design_version=design_version,
            )
            if candidate:
                candidates.append(candidate)

    return candidates


def extract_all_candidates(scenarios, project_root):
    """Phase 1: 从所有轨迹中提取候选数据"""
    all_candidates = []

    for scenario in scenarios:
        config = SCENARIO_CONFIGS[scenario]
        base_dir = os.path.join(project_root, config["base_dir"])
        criteria_dir = config["judge_criteria_dir"]

        # 加载 judge criteria
        all_criteria = load_judge_criteria(base_dir, criteria_dir)
        print(f"[{scenario.upper()}] 加载 {len(all_criteria)} 条 judge criteria", file=sys.stderr)

        # 查找 eval 目录
        eval_dirs = find_eval_dirs(base_dir, config["eval_patterns"])
        print(f"[{scenario.upper()}] 找到 {len(eval_dirs)} 个 eval 目录", file=sys.stderr)

        scenario_count = 0
        for eval_dir in eval_dirs:
            # 遍历样本文件
            for entry in sorted(os.listdir(eval_dir)):
                if not entry.endswith(".json") or entry == "execution_report.json":
                    continue
                sample_path = os.path.join(eval_dir, entry)
                sample_id = entry.replace(".json", "")
                env_dir = os.path.join(eval_dir, f"{sample_id}_env")

                if not os.path.isdir(env_dir):
                    continue

                candidates = extract_candidates_from_sample(
                    scenario, sample_path, env_dir, all_criteria
                )
                all_candidates.extend(candidates)
                scenario_count += len(candidates)

        print(f"[{scenario.upper()}] 提取 {scenario_count} 条候选数据", file=sys.stderr)

    return all_candidates


# ── 分层采样 ──────────────────────────────────────────────────────

LENGTH_BIN_TARGETS = {
    "10K-20K": 88,   # 80 * 1.1 = 88
    "20K-40K": 99,   # 90 * 1.1 = 99
    "40K-70K": 110,  # 100 * 1.1 = 110
    "70K-100K": 33,  # 30 * 1.1 = 33
}
# 总计：330 条（按 1.1 倍扩充，确保 pretrain 能有 300 条）


def stratified_sample(candidates, target_count, seed=42):
    """Phase 2: 分层采样"""
    random.seed(seed)

    # 过滤掉没有 judge_criteria 的候选（无法评判，无意义）
    candidates = [c for c in candidates if c.get("judge_criteria")]

    # 按 length_bin 分组
    by_bin = defaultdict(list)
    for c in candidates:
        by_bin[c["length_bin"]].append(c)

    # 计算每个 bin 的目标数量
    total_target_ratio = sum(LENGTH_BIN_TARGETS.values())
    bin_targets = {}
    for bin_name, ratio in LENGTH_BIN_TARGETS.items():
        bin_targets[bin_name] = max(1, int(target_count * ratio / total_target_ratio))

    # 确保总数接近 target_count
    assigned = sum(bin_targets.values())
    diff = target_count - assigned
    if diff > 0:
        # 把多余的分配给候选最多的 bin
        sorted_bins = sorted(bin_targets.keys(), key=lambda b: len(by_bin[b]), reverse=True)
        for i in range(diff):
            bin_targets[sorted_bins[i % len(sorted_bins)]] += 1

    sampled = []
    for bin_name in sorted(LENGTH_BIN_TARGETS.keys()):
        pool = by_bin[bin_name]
        target = bin_targets[bin_name]

        if not pool:
            print(f"  [WARN] {bin_name}: 无候选数据", file=sys.stderr)
            continue

        # 在 bin 内按 scenario 均匀、source_quality 70/30 分配
        selected = sample_within_bin(pool, target)
        sampled.extend(selected)
        print(f"  {bin_name}: 目标 {target}, 候选 {len(pool)}, 采样 {len(selected)}", file=sys.stderr)

    return sampled


def sample_within_bin(pool, target):
    """在一个 length_bin 内做分层采样

    策略：按模型分桶，round-robin 轮流从各模型中抽取，保证模型多样性。
    同时在每个模型内部按 scenario 交替，保证场景多样性。
    同一 (sample_id, model) 最多取 3 条。
    """
    if len(pool) <= target:
        return pool

    # 按模型分桶，每个模型内部按 scenario 交替排列
    by_model = defaultdict(list)
    for c in pool:
        by_model[c["source_model"]].append(c)

    for model in by_model:
        items = by_model[model]
        random.shuffle(items)
        # 按 scenario 分组后交替排列，增加场景多样性
        by_scenario = defaultdict(list)
        for c in items:
            by_scenario[c["scenario"]].append(c)
        interleaved = []
        scenario_iters = {s: iter(cs) for s, cs in by_scenario.items()}
        while scenario_iters:
            exhausted = []
            for s in sorted(scenario_iters.keys()):
                try:
                    interleaved.append(next(scenario_iters[s]))
                except StopIteration:
                    exhausted.append(s)
            for s in exhausted:
                del scenario_iters[s]
        by_model[model] = interleaved

    # 计算每个模型的配额
    available_models = sorted(by_model.keys())
    n_models = len(available_models)
    if n_models == 0:
        return []

    # 高质量模型稍多（1.3x），混合质量模型稍少（0.85x）
    high_count = sum(1 for m in available_models if m in HIGH_QUALITY_MODELS)
    mixed_count = n_models - high_count

    model_targets = {}
    if high_count > 0 and mixed_count > 0:
        total_shares = high_count * 1.3 + mixed_count * 0.85
        per_share = target / total_shares
        for m in available_models:
            if m in HIGH_QUALITY_MODELS:
                model_targets[m] = max(1, int(per_share * 1.3))
            else:
                model_targets[m] = max(1, int(per_share * 0.85))
    else:
        base = max(1, target // n_models)
        for m in available_models:
            model_targets[m] = base

    # 但不能超过该模型的实际候选数，也不超过 target 的 20%（防止单模型占比过大）
    max_per_model = max(3, int(target * 0.2))
    for m in available_models:
        model_targets[m] = min(model_targets[m], len(by_model[m]), max_per_model)

    # Round-robin 从各模型轮流抽取
    selected = []
    selected_ids = set()
    sample_counts = defaultdict(int)  # (sample_id, model) -> count
    model_picked = defaultdict(int)

    max_rounds = max(len(items) for items in by_model.values())
    for round_idx in range(max_rounds):
        if len(selected) >= target:
            break
        for model in available_models:
            if len(selected) >= target:
                break
            if model_picked[model] >= model_targets.get(model, 999):
                continue
            items = by_model[model]
            if round_idx >= len(items):
                continue
            c = items[round_idx]
            key = (c["source_sample_id"], c["source_model"])
            if sample_counts[key] >= 3:
                continue
            if c["id"] in selected_ids:
                continue
            selected.append(c)
            selected_ids.add(c["id"])
            sample_counts[key] += 1
            model_picked[model] += 1

    # 如果因配额限制还不够，放开模型配额做第二轮（但仍限制每模型不超过 max_per_model）
    if len(selected) < target:
        for model in available_models:
            if model_picked[model] >= max_per_model:
                continue
            items = by_model[model]
            for c in items:
                if len(selected) >= target:
                    break
                if model_picked[model] >= max_per_model:
                    break
                if c["id"] in selected_ids:
                    continue
                key = (c["source_sample_id"], c["source_model"])
                if sample_counts[key] >= 3:
                    continue
                selected.append(c)
                selected_ids.add(c["id"])
                sample_counts[key] += 1
                model_picked[model] += 1

    # 最后兜底：如果仍然不够（所有模型都已到上限），完全放开
    if len(selected) < target:
        all_remaining = [c for c in pool if c["id"] not in selected_ids]
        random.shuffle(all_remaining)
        for c in all_remaining:
            if len(selected) >= target:
                break
            key = (c["source_sample_id"], c["source_model"])
            if sample_counts[key] >= 3:
                continue
            selected.append(c)
            selected_ids.add(c["id"])

    return selected[:target]


# ── 输出 ──────────────────────────────────────────────────────────

def print_distribution(candidates, label="候选数据"):
    """打印分布统计"""
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"{label}分布统计 (共 {len(candidates)} 条)", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    # 按 length_bin
    by_bin = defaultdict(int)
    for c in candidates:
        by_bin[c["length_bin"]] += 1
    print(f"\n按长度区间:", file=sys.stderr)
    for b in ["under_10K", "10K-20K", "20K-40K", "40K-70K", "70K-100K"]:
        print(f"  {b}: {by_bin.get(b, 0)}", file=sys.stderr)

    # 按 scenario
    by_scenario = defaultdict(int)
    for c in candidates:
        by_scenario[c["scenario"]] += 1
    print(f"\n按场景:", file=sys.stderr)
    for s in sorted(by_scenario.keys()):
        print(f"  {s}: {by_scenario[s]}", file=sys.stderr)

    # 按 stage
    by_stage = defaultdict(int)
    for c in candidates:
        by_stage[f"{c['scenario']}/{c['stage']}"] += 1
    print(f"\n按阶段:", file=sys.stderr)
    for s in sorted(by_stage.keys()):
        print(f"  {s}: {by_stage[s]}", file=sys.stderr)

    # 按 source_quality
    by_quality = defaultdict(int)
    for c in candidates:
        by_quality[c["source_quality"]] += 1
    print(f"\n按来源质量:", file=sys.stderr)
    for q in sorted(by_quality.keys()):
        print(f"  {q}: {by_quality[q]}", file=sys.stderr)

    # 按 model
    by_model = defaultdict(int)
    for c in candidates:
        by_model[c["source_model"]] += 1
    print(f"\n按模型:", file=sys.stderr)
    for m in sorted(by_model.keys()):
        print(f"  {m}: {by_model[m]}", file=sys.stderr)

    # input_tokens 分布
    if candidates:
        tokens = [c["input_tokens_est"] for c in candidates]
        print(f"\ninput_tokens 分布:", file=sys.stderr)
        print(f"  min: {min(tokens)}", file=sys.stderr)
        print(f"  max: {max(tokens)}", file=sys.stderr)
        print(f"  avg: {sum(tokens)//len(tokens)}", file=sys.stderr)
        print(f"  median: {sorted(tokens)[len(tokens)//2]}", file=sys.stderr)

    # 有 judge_criteria 的比例
    with_criteria = sum(1 for c in candidates if c.get("judge_criteria"))
    print(f"\n有 judge_criteria: {with_criteria}/{len(candidates)}", file=sys.stderr)

    print(f"{'='*60}\n", file=sys.stderr)


def write_dataset(dataset, output_path):
    """写入 JSONL 文件"""
    with open(output_path, "w", encoding="utf-8") as f:
        for item in dataset:
            # 输出时去掉 system_prompt（已包含在 input 中）
            output_item = {k: v for k, v in item.items() if k != "system_prompt"}
            f.write(json.dumps(output_item, ensure_ascii=False) + "\n")
    print(f"写入 {len(dataset)} 条到 {output_path}", file=sys.stderr)


def generate_stats_report(dataset, output_path):
    """生成 Markdown 格式的统计报告"""
    n = len(dataset)
    lines = []
    lines.append(f"# 单轮长上下文评测数据集统计报告\n")
    lines.append(f"**总条数**: {n}\n")

    # ── 1. 输入长度分布 ──
    lines.append("## 1. 输入长度分布\n")
    by_bin = defaultdict(list)
    for c in dataset:
        by_bin[c["length_bin"]].append(c["input_tokens_est"])
    lines.append("| 长度区间 | 条数 | 占比 | 平均tokens | 最小tokens | 最大tokens |")
    lines.append("|----------|------|------|-----------|-----------|-----------|")
    for b in ["10K-20K", "20K-40K", "40K-70K", "70K-100K"]:
        tokens = by_bin.get(b, [])
        cnt = len(tokens)
        pct = f"{cnt/n*100:.1f}%"
        if tokens:
            avg = sum(tokens) // cnt
            lines.append(f"| {b} | {cnt} | {pct} | {avg:,} | {min(tokens):,} | {max(tokens):,} |")
        else:
            lines.append(f"| {b} | 0 | 0% | - | - | - |")

    all_tokens = [c["input_tokens_est"] for c in dataset]
    sorted_t = sorted(all_tokens)
    lines.append(f"\n**全局**: min={min(all_tokens):,}, max={max(all_tokens):,}, "
                 f"avg={sum(all_tokens)//n:,}, median={sorted_t[n//2]:,}\n")

    # ── 2. 产出物类型分布 ──
    lines.append("## 2. 产出物类型分布\n")
    by_type = defaultdict(int)
    for c in dataset:
        by_type[c["output_type"]] += 1
    lines.append("| 产出物类型 | 条数 | 占比 |")
    lines.append("|-----------|------|------|")
    for t in sorted(by_type.keys(), key=lambda x: -by_type[x]):
        cnt = by_type[t]
        lines.append(f"| {t} | {cnt} | {cnt/n*100:.1f}% |")

    # ── 3. 场景分布 ──
    lines.append("\n## 3. 场景分布\n")
    SCENARIO_NAMES = {"nwa": "NWA 小说创作", "nts": "NTS 小说改编剧本", "sd": "SD 短剧创作"}
    by_scenario = defaultdict(int)
    for c in dataset:
        by_scenario[c["scenario"]] += 1
    lines.append("| 场景 | 条数 | 占比 |")
    lines.append("|------|------|------|")
    for s in ["nwa", "nts", "sd"]:
        cnt = by_scenario.get(s, 0)
        name = SCENARIO_NAMES.get(s, s)
        lines.append(f"| {name} | {cnt} | {cnt/n*100:.1f}% |")

    # ── 4. 题材分布 ──
    lines.append("\n## 4. 题材分布\n")
    by_genre = defaultdict(int)
    for c in dataset:
        by_genre[f"{c['scenario']}/{c['genre']}"] += 1
    lines.append("| 场景/题材 | 条数 | 占比 |")
    lines.append("|----------|------|------|")
    for g in sorted(by_genre.keys(), key=lambda x: -by_genre[x]):
        cnt = by_genre[g]
        lines.append(f"| {g} | {cnt} | {cnt/n*100:.1f}% |")

    # ── 5. 来源模型分布 ──
    lines.append("\n## 5. 来源模型分布\n")
    by_model = defaultdict(int)
    for c in dataset:
        by_model[c["source_model"]] += 1
    lines.append("| 模型 | 质量等级 | 条数 | 占比 |")
    lines.append("|------|---------|------|------|")
    for m in sorted(by_model.keys(), key=lambda x: -by_model[x]):
        cnt = by_model[m]
        q = "high" if m in HIGH_QUALITY_MODELS else "mixed"
        lines.append(f"| {m} | {q} | {cnt} | {cnt/n*100:.1f}% |")

    by_quality = defaultdict(int)
    for c in dataset:
        by_quality[c["source_quality"]] += 1
    lines.append(f"\n**来源质量汇总**: high={by_quality.get('high',0)} ({by_quality.get('high',0)/n*100:.0f}%), "
                 f"mixed={by_quality.get('mixed',0)} ({by_quality.get('mixed',0)/n*100:.0f}%)\n")

    # ── 6. 模型 × 长度区间 交叉表 ──
    lines.append("## 6. 模型 × 长度区间 交叉表\n")
    by_model_bin = defaultdict(lambda: defaultdict(int))
    for c in dataset:
        by_model_bin[c["source_model"]][c["length_bin"]] += 1
    bins = ["10K-20K", "20K-40K", "40K-70K", "70K-100K"]
    header = "| 模型 | " + " | ".join(bins) + " | 合计 |"
    lines.append(header)
    lines.append("|" + "------|" * (len(bins) + 2))
    for m in sorted(by_model_bin.keys(), key=lambda x: -sum(by_model_bin[x].values())):
        row_bins = by_model_bin[m]
        total = sum(row_bins.values())
        vals = " | ".join(str(row_bins.get(b, 0)) for b in bins)
        lines.append(f"| {m} | {vals} | {total} |")

    # ── 7. Reference Output 长度分布 ──
    lines.append("\n## 7. Reference Output 长度分布\n")
    ref_tokens = [c["reference_output_tokens_est"] for c in dataset]
    ref_sorted = sorted(ref_tokens)
    lines.append(f"- **min**: {min(ref_tokens):,} tokens")
    lines.append(f"- **max**: {max(ref_tokens):,} tokens")
    lines.append(f"- **avg**: {sum(ref_tokens)//n:,} tokens")
    lines.append(f"- **median**: {ref_sorted[n//2]:,} tokens")

    ref_bins = {"<1K": 0, "1K-3K": 0, "3K-5K": 0, "5K-10K": 0, ">10K": 0}
    for t in ref_tokens:
        if t < 1000:
            ref_bins["<1K"] += 1
        elif t < 3000:
            ref_bins["1K-3K"] += 1
        elif t < 5000:
            ref_bins["3K-5K"] += 1
        elif t < 10000:
            ref_bins["5K-10K"] += 1
        else:
            ref_bins[">10K"] += 1
    lines.append("\n| 区间 | 条数 | 占比 |")
    lines.append("|------|------|------|")
    for b, cnt in ref_bins.items():
        lines.append(f"| {b} | {cnt} | {cnt/n*100:.1f}% |")

    # ── 8. Judge Criteria 覆盖情况 ──
    lines.append("\n## 8. Judge Criteria 覆盖情况\n")
    has_criteria = sum(1 for c in dataset if c.get("has_judge_criteria"))
    lines.append(f"- **有 judge criteria**: {has_criteria}/{n} ({has_criteria/n*100:.1f}%)")
    lines.append(f"- **无 judge criteria**: {n-has_criteria}/{n}")
    if has_criteria:
        jc_counts = [c["judge_criteria_count"] for c in dataset if c.get("has_judge_criteria")]
        lines.append(f"- **criteria 数量分布**: min={min(jc_counts)}, max={max(jc_counts)}, avg={sum(jc_counts)//len(jc_counts)}")

    lines.append("\n按产出物类型:")
    lines.append("\n| 产出物类型 | 有criteria | 无criteria |")
    lines.append("|-----------|-----------|-----------|")
    type_criteria = defaultdict(lambda: [0, 0])
    for c in dataset:
        ot = c["output_type"]
        if c.get("has_judge_criteria"):
            type_criteria[ot][0] += 1
        else:
            type_criteria[ot][1] += 1
    for ot in sorted(type_criteria.keys()):
        y, n_ = type_criteria[ot]
        lines.append(f"| {ot} | {y} | {n_} |")

    # ── 9. 章节/集数编号分布（仅限章节/剧本类） ──
    lines.append("\n## 9. 章节/集数编号分布\n")
    seq_items = [(c["output_type"], c["sequence_num"]) for c in dataset if c.get("sequence_num") is not None]
    by_type_seq = defaultdict(list)
    for ot, sn in seq_items:
        by_type_seq[ot].append(sn)
    for ot in sorted(by_type_seq.keys()):
        nums = sorted(by_type_seq[ot])
        lines.append(f"**{ot}** ({len(nums)} 条): 范围 {min(nums)}~{max(nums)}, "
                     f"平均 {sum(nums)//len(nums)}, 中位数 {nums[len(nums)//2]}")

    # ── 10. 设计版本分布 ──
    lines.append("\n## 10. 设计版本分布\n")
    by_dv = defaultdict(int)
    for c in dataset:
        by_dv[c["design_version"]] += 1
    lines.append("| 设计版本 | 条数 | 占比 |")
    lines.append("|---------|------|------|")
    for dv in sorted(by_dv.keys()):
        cnt = by_dv[dv]
        lines.append(f"| {dv} | {cnt} | {cnt/n*100:.1f}% |")

    # 写入文件
    report_text = "\n".join(lines) + "\n"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"统计报告写入 {output_path}", file=sys.stderr)
    return report_text


# ── 入口 ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Agent 评测轨迹 → 单轮长上下文数据集")
    parser.add_argument("--scenarios", type=str, default="nwa,nts,sd",
                        help="要处理的场景，逗号分隔 (nwa,nts,sd)")
    parser.add_argument("--output", type=str, default="singleturn_dataset.jsonl",
                        help="输出 JSONL 文件路径")
    parser.add_argument("--target-count", type=int, default=150,
                        help="目标数据条数")
    parser.add_argument("--dry-run", action="store_true",
                        help="只统计分布，不输出数据")
    parser.add_argument("--stats", type=str, default=None,
                        help="输出 Markdown 统计报告的路径")
    parser.add_argument("--seed", type=int, default=42,
                        help="随机种子")
    args = parser.parse_args()

    scenarios = [s.strip() for s in args.scenarios.split(",")]
    for s in scenarios:
        if s not in SCENARIO_CONFIGS:
            print(f"错误: 未知场景 '{s}'，可用: {list(SCENARIO_CONFIGS.keys())}", file=sys.stderr)
            sys.exit(1)

    # 确定项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print(f"项目根目录: {project_root}", file=sys.stderr)
    print(f"处理场景: {scenarios}", file=sys.stderr)
    print(f"目标数据条数: {args.target_count}", file=sys.stderr)
    print(f"随机种子: {args.seed}", file=sys.stderr)

    # 加载单轮版 system prompts
    load_singleturn_system_prompts(project_root)
    print(f"加载 {len(SINGLETURN_SYSTEM_PROMPTS)} 个单轮版 system prompt", file=sys.stderr)

    # Phase 1: Extract
    print(f"\n{'='*60}", file=sys.stderr)
    print("Phase 1: 提取候选数据", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)
    candidates = extract_all_candidates(scenarios, project_root)

    if not candidates:
        print("错误: 未找到任何候选数据", file=sys.stderr)
        sys.exit(1)

    print_distribution(candidates, "候选数据")

    if args.dry_run:
        print("(dry-run 模式，不输出数据)", file=sys.stderr)
        return

    # Phase 2: Sample
    print(f"\n{'='*60}", file=sys.stderr)
    print("Phase 2: 分层采样", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)
    dataset = stratified_sample(candidates, args.target_count, seed=args.seed)
    print_distribution(dataset, "采样后数据")

    # Phase 3: Output
    print(f"\n{'='*60}", file=sys.stderr)
    print("Phase 3: 输出数据集", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)
    write_dataset(dataset, args.output)

    # Phase 4: Stats report
    if args.stats:
        print(f"\n{'='*60}", file=sys.stderr)
        print("Phase 4: 生成统计报告", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)
        generate_stats_report(dataset, args.stats)


if __name__ == "__main__":
    main()
