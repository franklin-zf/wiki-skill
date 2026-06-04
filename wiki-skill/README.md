# 名词 Wiki

面向 LLM 的业务术语知识库，服务于字节跳动流量场景、抖音、生活服务、团购、商家商品、直播、电商、内容安全、机审运营等场景的 PE（Prompt Engineering）设计。

每个名词可绑定：

- `scenarios`：业务/治理/经营场景。
- `industries`：行业或业务域。
- `tags`：检索标签、指标、判定项、链路节点。
- `premise`：判定前提、边界、公式、豁免、来源不确定性。

## 核心原则

- 本质：给 LLM 喂的结构化术语知识，不是业务规则的替代品。
- 零依赖：`wiki.py` 仅用 Python 标准库。
- 可版本化：数据是 JSON，可 diff、可审查、可回滚。
- 小模型友好：执行链路写在 [references/global-rules.md](references/global-rules.md)，每个阶段都有输入、输出、约束和停止条件。

## 目录结构

```text
wiki-skill/
├── SKILL.md
├── agents/openai.yaml
├── references/
│   └── global-rules.md
├── wiki.py
├── data/
│   ├── terms.json
│   └── scenarios.json
└── README.md
```

## 快速开始

```bash
cd wiki-skill

python3 wiki.py scenarios
python3 wiki.py stats
python3 wiki.py validate

python3 wiki.py query -k POI
python3 wiki.py query -s 机审场景 -f prompt
python3 wiki.py query -i 生活服务 -k M2
python3 wiki.py query -s 流量场景 -t 流量分层 -f prompt
```

## 业务流归纳

当用户要求“归纳业务流”“整理链路”“给小模型可执行规则”时，按 [references/global-rules.md](references/global-rules.md) 输出：

```markdown
## 业务流：<name>

- 输入：<facts, documents, signals, user request, source fields>
- 处理：<ordered steps or transformation logic>
- 输出：<labels, definitions, prompt fragments, decisions, reports>
- 约束：<source priority, scenario boundary, validity, required premise>
- 风险：<ambiguity, missing source, conflicting term, pending validity>
- 校验：<query/validate commands or manual coverage checks>
```

## 来源策略

| 类型 | 来源 | 有效性 |
| --- | --- | --- |
| 用户提供的官方/内部整理文档 | `source_type=user/internal` | 可标 `verified` |
| 官方或一手公开来源 | `source_type=web` | 核验后可标 `verified` |
| 第三方公开文章、行业经验、未内部确认口径 | `source_type=web` | 默认 `pending` |

公开 Web 来源若不是官方/内部口径，应在 `premise` 或 `meta.source_note` 中标明“公开来源口径/待内部校准”。

## 验证

```bash
python3 wiki.py validate
python3 /Users/zhangfeng/.codex/skills/.system/skill-creator/scripts/quick_validate.py <wiki-skill目录>
```
