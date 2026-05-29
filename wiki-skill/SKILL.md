---
name: wiki-skill
description: >-
  名词 Wiki —— 面向 LLM 的名词解释知识库，用于机审/直播/电商/生活服务等场景的 PE（Prompt Engineering）设计。
  当需要解释直播术语、经营术语、机审判定项、行业名词，或为流量场景拼装名词解释 prompt 片段，
  或用户要求新增/查询/校验名词时使用。触发词：wiki-skill、名词wiki、名词解释、术语解释、机审名词、
  店铺环境判定、营销信息、憋单、福袋、过款、控场、导流术语、给LLM喂名词。
---

# Wiki Skill（名词 Wiki）

结构化、可版本化、面向 LLM 的名词知识库。每个名词关联行业/场景，可携带判定前提/边界，服务于机审 PE 设计。

## 定位本 Skill 的数据目录

优先使用以下路径（按顺序尝试）：

1. **本 skill 安装目录**（Codex：`~/.codex/skills/wiki-skill/`；克隆仓库后的 `wiki-skill/`）
2. **当前仓库根目录下的 `wiki-skill/`**（若在 monorepo 中）

进入数据目录后执行 CLI：

```bash
cd <wiki-skill目录>
python3 wiki.py <子命令>
```

## 子命令速查

### 查询（PE 拼装最常用）

```bash
python3 wiki.py query -k 憋单
python3 wiki.py query -s 机审场景
python3 wiki.py query -s 机审场景 -f prompt   # 可直接嵌入 system prompt
python3 wiki.py query -k 店铺 -f json
```

### 新增

- **通用行业术语**：先 web 检索验证 → `--source-type web --validity verified --source <URL>`
- **内部机审规则**：用户录入 → `--source-type user`，边界写入 `--premise`

```bash
python3 wiki.py add \
  --name "起号" \
  --definition "新开直播账号通过内容/投流快速度过冷启动、积累初始流量与标签的过程。" \
  --scenarios "直播术语,经营术语" \
  --aliases "冷启动" \
  --source "https://example.com" --source-type web --validity verified
```

默认 `validity=pending`；机审类务必填 `--premise`。

### 校验与统计

```bash
python3 wiki.py validate
python3 wiki.py scenarios
python3 wiki.py stats
```

## 词条 Schema

```json
{
  "id": "t_xxx",
  "name": "名词",
  "aliases": ["别名"],
  "definition": "面向 LLM 的精确定义",
  "scenarios": ["机审场景", "商家商品"],
  "premise": "判定前提/边界（可空）",
  "meta": {
    "source": "URL 或 用户录入",
    "source_type": "web | user | internal",
    "validity": "verified | pending | deprecated",
    "version": 1,
    "created_at": "2026-05-29",
    "updated_at": "2026-05-29",
    "updated_by": "user"
  }
}
```

## 工作流约定

1. 通用术语：web 检索 → 判断真实有效 → `add ... --validity verified`
2. 机审规则：用户录入 → `--premise` 写清边界
3. 任何变更后执行 `python3 wiki.py validate`
4. 新场景先在 `data/scenarios.json` 注册，或 `add --allow-new-scenario`

## GitHub

仓库：https://github.com/franklin-zf/wiki-skill（安装：`git clone` 后 `cd wiki-skill` 即可使用）
