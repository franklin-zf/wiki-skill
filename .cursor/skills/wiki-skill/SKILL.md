---
name: wiki-skill
description: >-
  名词 Wiki —— 面向 LLM 的名词解释知识库，用于机审/直播/电商/生活服务等场景的 PE 设计。
  当需要解释直播术语、经营术语、机审判定项、行业名词，或为流量场景拼装名词解释 prompt 片段，
  或用户要求新增/查询/校验名词时使用。触发词：wiki-skill、名词wiki、名词解释、术语解释、机审名词、
  店铺环境判定、营销信息、憋单、福袋、过款、控场、导流术语、给LLM喂名词。
---

# Wiki Skill（名词 Wiki）

与 Codex skill `wiki-skill` 同源。数据与 CLI 位于仓库 `wiki-skill/` 目录。

## 使用

```bash
cd wiki-skill   # 相对于仓库根 /Users/zhangfeng/Downloads/bytedance
python3 wiki.py query -s 机审场景 -f prompt
python3 wiki.py add --name "..." --definition "..." --scenarios "机审场景" --premise "..."
python3 wiki.py validate
```

完整说明见 `wiki-skill/SKILL.md` 与 `wiki-skill/README.md`。
