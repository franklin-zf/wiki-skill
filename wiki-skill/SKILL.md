---
name: wiki-skill
description: >-
  名词 Wiki —— 面向 LLM 的业务术语知识库和 prompt 术语对齐工具，用于字节跳动流量场景、
  抖音、生活服务、团购、商家商品、直播、电商、内容安全、机审运营等场景的 PE
  （Prompt Engineering）设计。用于查询/新增/导入/校验名词，按场景、行业、标签拼装
  prompt 术语片段，或把业务链路中的输入、输出、约束、风险和判定边界结构化。
  触发词：wiki-skill、名词wiki、名词解释、术语解释、业务流归纳、机审名词、生活服务名词、
  电商商品名词、流量分层、POI、核销、泛导流、实景直播、Dryrun、M1、M2、M3、给LLM喂名词。
---

# Wiki Skill（名词 Wiki）

结构化、可版本化、面向 LLM 的业务术语知识库。每个名词关联 `scenarios`、`industries`、`tags`，可携带来源、有效性、判定前提和业务边界。

## 必读规则

所有查询、新增、导入、校验、业务流归纳任务都必须先按 [references/global-rules.md](references/global-rules.md) 执行。该文件是全局规则文档，定义：

- 任务分类。
- 每个阶段的输入、输出、约束、停止条件。
- 小模型友好的固定工作流。
- 业务流归纳的标准产物。
- 交付格式和验证门槛。

不要跳过全局规则直接凭印象解释术语。

## 定位数据目录

按顺序尝试：

1. 本 skill 安装目录：`~/.codex/skills/wiki-skill/`
2. 当前仓库根目录下的 `wiki-skill/`

成功定位的目录必须包含：

```text
SKILL.md
wiki.py
data/terms.json
data/scenarios.json
references/global-rules.md
```

## 任务类型

每次只选择一个主任务：

- `query`：查询名词定义、别名、来源、边界。
- `prompt-fragment`：按场景/行业/标签拼装可放入 system prompt 的术语片段。
- `business-flow`：围绕业务链路输出输入、处理、输出、约束、风险、校验点。
- `add-term`：新增单个词条。
- `import-terms`：从用户文档批量导入词条。
- `validate-stats`：校验、统计、列出场景。
- `blocked`：缺少来源、场景、边界或权限，继续会导致猜测。

意图不清时先问；不要同时做多个主任务。

## CLI 速查

```bash
cd <wiki-skill目录>

python3 wiki.py scenarios
python3 wiki.py stats
python3 wiki.py validate

python3 wiki.py query -k 憋单
python3 wiki.py query -s 机审场景
python3 wiki.py query -s 流量场景 -t 流量分层 -f prompt
python3 wiki.py query -i 生活服务 -k M2
python3 wiki.py query -k 店铺 -f json
```

新增词条优先使用 CLI：

```bash
python3 wiki.py add \
  --name "起号" \
  --definition "新开直播账号通过内容/投流快速度过冷启动、积累初始流量与标签的过程。" \
  --scenarios "直播术语,经营术语" \
  --industries "抖音电商,生活服务" \
  --tags "冷启动,账号经营,流量获取" \
  --aliases "冷启动" \
  --premise "适用于账号冷启动语境；不同业务线如有内部口径，以内部规则为准。" \
  --source "https://example.com" --source-type web --validity pending
```

## Schema 摘要

```json
{
  "id": "t_xxx",
  "name": "名词",
  "aliases": ["别名"],
  "definition": "面向 LLM 的精确定义",
  "scenarios": ["机审场景", "商家商品"],
  "industries": ["生活服务"],
  "tags": ["店铺环境", "商家资质"],
  "premise": "判定前提/边界（可空）",
  "meta": {
    "source": "URL 或用户录入",
    "source_type": "web | user | internal",
    "validity": "verified | pending | deprecated",
    "version": 1,
    "created_at": "2026-05-29",
    "updated_at": "2026-05-29",
    "updated_by": "user"
  }
}
```

## 硬约束

- Wiki 只解释术语和业务边界，不替代用户规则、节点 prompt、坏例、内部规则或审核标准。
- 没有来源的词条不得标 `verified`。
- Web 来源不是官方/内部口径时，必须在 `premise` 或 `meta.source_note` 标明“公开来源口径/待内部校准”。
- 同名词在不同场景含义不同时，不要压成一个通用定义；用 `scenarios`、`industries`、`tags` 和 `premise` 写清边界。
- 查询先于新增；命中冲突时停止合并并报告冲突。
- 任何数据变更后必须运行 `python3 wiki.py validate`。未验证不得声称完成。

## 交付格式

最终回复保持简洁，必须包含：

- 改了什么或查到了什么。
- 使用的文件/命令。
- 数据有效性和来源状态。
- 验证结果。
- 未覆盖风险或需用户确认项。
