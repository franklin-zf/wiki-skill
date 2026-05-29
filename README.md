# wiki-skill

面向 LLM 的名词解释知识库，用于机审 / 直播 / 电商 / 生活服务等场景的 PE（Prompt Engineering）设计。

## 结构

```
wiki-skill/          # 数据 + CLI + Codex Skill 主目录
├── SKILL.md
├── agents/openai.yaml
├── wiki.py
├── data/
│   ├── terms.json
│   └── scenarios.json
└── README.md
.cursor/skills/wiki-skill/   # Cursor 项目级 skill 入口
```

## 快速开始

```bash
cd wiki-skill
python3 wiki.py scenarios
python3 wiki.py query -s 机审场景 -f prompt
python3 wiki.py validate
```

## 安装为 Codex Skill

```bash
git clone https://github.com/franklin-zf/wiki-skill.git
cp -R wiki-skill ~/.codex/skills/wiki-skill
# 或仅克隆后直接在仓库内使用
```

## License

MIT
