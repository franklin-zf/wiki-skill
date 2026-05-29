# 名词 Wiki（已迁移）

> **已迁移至 [`../wiki-skill/`](../wiki-skill/)**。请使用新目录与 `wiki-skill` skill。

面向 LLM 的名词解释知识库，服务于机审 / 直播 / 电商 / 生活服务等场景的 PE（Prompt Engineering）设计。每个名词关联所属行业/场景，并可携带"判定前提/边界条件"。

## 设计取舍（第一性原理）

- **本质**：给 LLM 喂的、结构化、可被检索的名词知识。所以用纯数据文件存储，而非数据库或 Web 应用。
- **零依赖**：`wiki.py` 仅用 Python 标准库，任意环境 `python3 wiki.py` 即可运行，便于被 skill/CI/LLM 调用。
- **可版本化**：数据是 JSON，天然可 diff、可 Code Review、可回滚。
- **数据与代码解耦**：数据在 `data/`，逻辑在 `wiki.py`。

## 目录结构

```
名词wiki/
├── data/
│   ├── terms.json       # 词条库
│   └── scenarios.json   # 场景分类法（受控词表）
├── wiki.py              # 查询 / 新增 / 校验 CLI
└── README.md
```

## 快速开始

```bash
cd 名词wiki
python3 wiki.py scenarios                  # 看有哪些场景
python3 wiki.py query -s 机审场景           # 查某场景全部名词
python3 wiki.py query -k 憋单               # 关键词检索
python3 wiki.py query -s 机审场景 -f prompt # 导出可嵌入 prompt 的片段
python3 wiki.py validate                   # 校验全库
```

## 名词来源策略（混合）

| 类型 | 来源 | 录入方式 |
| --- | --- | --- |
| 通用行业/直播/电商术语 | Web 检索 + 验证 | `add --source <URL> --source-type web --validity verified` |
| 内部机审规则类名词 | 用户提供 | `add --source-type user`，规则边界写入 `--premise` |

新增词条默认 `validity=pending`，人工确认真实有效后改为 `verified`。

## 给 LLM/Skill 用

见 `/.cursor/skills/term-wiki/SKILL.md`。典型用法：为某流量场景拼装 PE 时，
`python3 wiki.py query -s <场景> -f prompt` 取该场景全部名词解释直接拼进系统提示。
