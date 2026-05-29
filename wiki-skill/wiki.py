#!/usr/bin/env python3
"""名词 Wiki：面向 LLM 的名词解释知识库的查询/录入/校验命令行工具。

设计原则：纯标准库、单文件、数据与代码解耦（数据在 data/*.json），
便于版本化、便于被 skill / LLM 调用。
"""
import argparse
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"
TERMS_FILE = DATA_DIR / "terms.json"
SCENARIOS_FILE = DATA_DIR / "scenarios.json"

REQUIRED_TERM_FIELDS = ["id", "name", "definition", "scenarios", "meta"]
REQUIRED_META_FIELDS = [
    "source", "source_type", "validity", "version", "created_at", "updated_at",
]
VALID_VALIDITY = {"verified", "pending", "deprecated"}
VALID_SOURCE_TYPE = {"web", "user", "internal"}


def _load(path):
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save(path, data):
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def load_terms():
    data = _load(TERMS_FILE)
    return data.get("terms", []), data


def load_scenarios():
    data = _load(SCENARIOS_FILE)
    return data.get("scenarios", [])


def _norm(s):
    return re.sub(r"\s+", "", (s or "").strip().lower())


def _all_names(term):
    return [term.get("name", "")] + list(term.get("aliases", []) or [])


def _scenario_name_set():
    return {s["name"] for s in load_scenarios()} | {s["id"] for s in load_scenarios()}


def make_id(name):
    return "t_" + hashlib.md5(name.encode("utf-8")).hexdigest()[:10]


# ---------------------------------------------------------------- query
def _match(term, keyword, scenario, validity):
    if validity and term.get("meta", {}).get("validity") != validity:
        return False
    if scenario:
        scs = term.get("scenarios", [])
        if scenario not in scs and _norm(scenario) not in [_norm(x) for x in scs]:
            return False
    if keyword:
        k = _norm(keyword)
        haystack = _norm(term.get("name", "")) + _norm(term.get("definition", "")) \
            + _norm(term.get("premise", "")) + "".join(_norm(a) for a in term.get("aliases", []) or [])
        if k not in haystack:
            return False
    return True


def render_md(term):
    aliases = "、".join(term.get("aliases", []) or [])
    alias_str = f"（别名：{aliases}）" if aliases else ""
    lines = [f"### {term['name']}{alias_str}"]
    lines.append(f"- **所属场景**：{ '、'.join(term.get('scenarios', [])) }")
    lines.append(f"- **定义**：{term.get('definition', '')}")
    if term.get("premise"):
        lines.append(f"- **判定前提/边界**：{term['premise']}")
    meta = term.get("meta", {})
    lines.append(
        f"- _来源：{meta.get('source', '?')}｜有效性：{meta.get('validity', '?')}"
        f"｜v{meta.get('version', '?')}｜更新：{meta.get('updated_at', '?')}_"
    )
    return "\n".join(lines)


def render_prompt(term):
    """精简、可直接嵌入 system prompt 的一行解释。"""
    aliases = term.get("aliases", []) or []
    name = term["name"]
    if aliases:
        name = f"{name}（亦称：{ '、'.join(aliases) }）"
    s = f"- 【{name}】{term.get('definition', '')}"
    if term.get("premise"):
        s += f" 判定前提：{term['premise']}"
    return s


def cmd_query(args):
    terms, _ = load_terms()
    hits = [t for t in terms if _match(t, args.keyword, args.scenario, args.validity)]
    if args.format == "json":
        print(json.dumps(hits, ensure_ascii=False, indent=2))
        return 0
    if not hits:
        print("（无匹配词条）", file=sys.stderr)
        return 1
    if args.format == "prompt":
        header = "## 名词解释"
        if args.scenario:
            header += f"（场景：{args.scenario}）"
        print(header)
        for t in hits:
            print(render_prompt(t))
        return 0
    # markdown (default)
    print(f"# 名词 Wiki 查询结果（命中 {len(hits)} 条）\n")
    for t in hits:
        print(render_md(t))
        print()
    return 0


# ---------------------------------------------------------------- add
def _build_term_from_args(args):
    name = args.name.strip()
    scenarios = [s.strip() for s in args.scenarios.split(",") if s.strip()]
    aliases = [a.strip() for a in (args.aliases or "").split(",") if a.strip()]
    today = date.today().isoformat()
    return {
        "id": make_id(name),
        "name": name,
        "aliases": aliases,
        "definition": args.definition.strip(),
        "scenarios": scenarios,
        "premise": (args.premise or "").strip(),
        "meta": {
            "source": args.source or "用户录入",
            "source_type": args.source_type,
            "validity": args.validity,
            "version": 1,
            "created_at": today,
            "updated_at": today,
            "updated_by": args.updated_by or "user",
        },
    }


def _find_duplicate(new_term, terms):
    new_names = {_norm(n) for n in _all_names(new_term) if n}
    for t in terms:
        existing = {_norm(n) for n in _all_names(t) if n}
        if new_names & existing:
            return t
    return None


def cmd_add(args):
    if args.json:
        new_term = json.loads(args.json)
    elif args.json_file:
        new_term = json.loads(Path(args.json_file).read_text(encoding="utf-8"))
    else:
        if not (args.name and args.definition and args.scenarios):
            print("错误：缺少必填项。需提供 --name --definition --scenarios，或用 --json/--json-file。", file=sys.stderr)
            return 2
        new_term = _build_term_from_args(args)

    # 校验场景合法性
    known = _scenario_name_set()
    unknown = [s for s in new_term.get("scenarios", []) if s not in known]
    if unknown and not args.allow_new_scenario:
        print(f"错误：未知场景 {unknown}。已知场景：{sorted(known)}。"
              f"如确需新增场景请加 --allow-new-scenario 或先在 scenarios.json 注册。", file=sys.stderr)
        return 2

    errors = validate_term(new_term)
    if errors:
        print("错误：词条 schema 校验未通过：\n  - " + "\n  - ".join(errors), file=sys.stderr)
        return 2

    terms, data = load_terms()
    dup = _find_duplicate(new_term, terms)
    if dup:
        print(f"错误：与已有词条重复（名词/别名冲突）：{dup['name']} (id={dup['id']})。"
              f"如需更新请直接编辑 data/terms.json 或后续提供 update 能力。", file=sys.stderr)
        return 3

    terms.append(new_term)
    data["terms"] = terms
    data["updated_at"] = date.today().isoformat()
    _save(TERMS_FILE, data)
    print(f"已新增词条：{new_term['name']} (id={new_term['id']})，当前共 {len(terms)} 条。")
    return 0


# ---------------------------------------------------------------- validate
def validate_term(term):
    errors = []
    for f in REQUIRED_TERM_FIELDS:
        if f not in term or term[f] in (None, "", []):
            errors.append(f"缺少必填字段 `{f}`")
    if not isinstance(term.get("scenarios", []), list) or not term.get("scenarios"):
        errors.append("`scenarios` 必须是非空列表")
    meta = term.get("meta", {})
    if not isinstance(meta, dict):
        errors.append("`meta` 必须是对象")
    else:
        for f in REQUIRED_META_FIELDS:
            if f not in meta or meta[f] in (None, ""):
                errors.append(f"meta 缺少字段 `{f}`")
        if meta.get("validity") and meta["validity"] not in VALID_VALIDITY:
            errors.append(f"meta.validity 非法：{meta['validity']}（应为 {VALID_VALIDITY}）")
        if meta.get("source_type") and meta["source_type"] not in VALID_SOURCE_TYPE:
            errors.append(f"meta.source_type 非法：{meta['source_type']}（应为 {VALID_SOURCE_TYPE}）")
    return errors


def cmd_validate(args):
    terms, _ = load_terms()
    known = _scenario_name_set()
    total_errors = 0
    seen = {}
    for i, t in enumerate(terms):
        errs = validate_term(t)
        for s in t.get("scenarios", []):
            if s not in known:
                errs.append(f"引用了未注册场景 `{s}`")
        for n in _all_names(t):
            key = _norm(n)
            if not key:
                continue
            if key in seen and seen[key] != t["id"]:
                errs.append(f"名词/别名 `{n}` 与词条 id={seen[key]} 重复")
            seen[key] = t["id"]
        if errs:
            total_errors += len(errs)
            print(f"[FAIL] #{i} {t.get('name', '?')} (id={t.get('id', '?')}):")
            for e in errs:
                print(f"    - {e}")
    if total_errors == 0:
        print(f"[OK] 全部 {len(terms)} 条词条校验通过，无重复、schema 合法。")
        return 0
    print(f"\n共发现 {total_errors} 个问题。", file=sys.stderr)
    return 1


# ---------------------------------------------------------------- scenarios / stats
def cmd_scenarios(args):
    scenarios = load_scenarios()
    terms, _ = load_terms()
    counts = {}
    for t in terms:
        for s in t.get("scenarios", []):
            counts[s] = counts.get(s, 0) + 1
    print("# 场景分类法\n")
    for s in scenarios:
        c = counts.get(s["name"], 0)
        print(f"- **{s['name']}** (`{s['id']}`) — {s['description']}  [{c} 条]")
    return 0


def cmd_stats(args):
    terms, _ = load_terms()
    by_validity, by_source = {}, {}
    for t in terms:
        m = t.get("meta", {})
        by_validity[m.get("validity", "?")] = by_validity.get(m.get("validity", "?"), 0) + 1
        by_source[m.get("source_type", "?")] = by_source.get(m.get("source_type", "?"), 0) + 1
    print(f"词条总数：{len(terms)}")
    print(f"按有效性：{by_validity}")
    print(f"按来源类型：{by_source}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(description="名词 Wiki：面向 LLM 的名词解释知识库")
    sub = p.add_subparsers(dest="cmd", required=True)

    q = sub.add_parser("query", help="检索词条")
    q.add_argument("--keyword", "-k", help="关键词（匹配名词/别名/定义/前提）")
    q.add_argument("--scenario", "-s", help="按场景过滤（场景名或 id）")
    q.add_argument("--validity", help="按有效性过滤：verified/pending/deprecated")
    q.add_argument("--format", "-f", choices=["md", "json", "prompt"], default="md",
                   help="输出格式：md(默认)/json/prompt(可嵌入系统提示)")
    q.set_defaults(func=cmd_query)

    a = sub.add_parser("add", help="新增词条")
    a.add_argument("--name", help="名词")
    a.add_argument("--definition", help="面向 LLM 的定义")
    a.add_argument("--scenarios", help="所属场景，逗号分隔")
    a.add_argument("--aliases", help="别名，逗号分隔", default="")
    a.add_argument("--premise", help="判定前提/边界条件", default="")
    a.add_argument("--source", help="来源（URL 或说明）", default="")
    a.add_argument("--source-type", dest="source_type", choices=sorted(VALID_SOURCE_TYPE),
                   default="user", help="来源类型")
    a.add_argument("--validity", choices=sorted(VALID_VALIDITY), default="pending",
                   help="有效性标记（默认 pending，校验真实有效后再标 verified）")
    a.add_argument("--updated-by", dest="updated_by", help="录入人", default="user")
    a.add_argument("--json", help="直接传入完整词条 JSON 字符串")
    a.add_argument("--json-file", dest="json_file", help="从 JSON 文件读取完整词条")
    a.add_argument("--allow-new-scenario", action="store_true", help="允许引用未注册场景")
    a.set_defaults(func=cmd_add)

    v = sub.add_parser("validate", help="全库 schema 校验 + 重复检测")
    v.set_defaults(func=cmd_validate)

    s = sub.add_parser("scenarios", help="列出场景分类法及词条计数")
    s.set_defaults(func=cmd_scenarios)

    st = sub.add_parser("stats", help="统计信息")
    st.set_defaults(func=cmd_stats)
    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
