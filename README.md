# wiki-skill

面向 LLM 的业务术语知识库，用于字节跳动流量场景、抖音、生活服务、团购、商家商品、直播、电商、内容安全、机审运营等场景的 PE（Prompt Engineering）设计。

## 结构

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
python3 wiki.py query -s 机审场景 -f prompt
python3 wiki.py validate
```

## 全局规则

弱模型或新 agent 使用本 skill 时，先读：

```text
wiki-skill/references/global-rules.md
```

该文档定义查询、新增、导入、业务流归纳、校验和交付的固定阶段，并明确每个阶段的输入、输出、约束和停止条件。

## 安装为 Codex Skill

```bash
git clone https://github.com/franklin-zf/wiki-skill.git
cp -R wiki-skill ~/.codex/skills/wiki-skill
```

## License

MIT
