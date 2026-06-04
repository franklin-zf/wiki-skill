# Wiki Skill Global Rules

This is the global operating contract for `wiki-skill`. Follow it before every query, prompt-fragment, term import, term creation, validation, and business-flow summary.

The goal is deterministic output on weaker models: every stage has explicit inputs, outputs, constraints, and stop conditions.

## Authority Order

When sources conflict, use this order:

1. User-provided current task instructions.
2. Local rule documents, node prompts, badcases, or internal source documents supplied by the user.
3. Existing `wiki-skill` entries with `validity=verified`.
4. Existing `wiki-skill` entries with `validity=pending`.
5. Public web sources.
6. Model inference.

Never let wiki terminology override source rules. If a wiki definition conflicts with a user rule or source document, report the conflict and let the source document win.

## Task Classifier

Choose exactly one main task.

| Task | Trigger | Main Output |
| --- | --- | --- |
| `query` | User asks what a term means or asks for aliases/boundaries | Matched term definitions with source and validity |
| `prompt-fragment` | User asks to feed terms to an LLM or build PE context | Compact `- 【term】definition` prompt block |
| `business-flow` | User asks to summarize a业务流/链路/流程/规则流 | Structured flow: inputs, processing, outputs, constraints, risks |
| `add-term` | User asks to add one term | One validated term entry |
| `import-terms` | User provides a document/dictionary to integrate | Added terms plus coverage and validation evidence |
| `validate-stats` | User asks to inspect wiki health or categories | Validation, stats, scenario counts |
| `blocked` | Required source, scenario, definition, or permission is missing | Short blocker report and concrete question |

If the user asks for multiple actions, do the smallest action that satisfies the request. If order matters, run `query` or `validate-stats` before writing.

## Stage Contract

| Stage | Input | Output | Constraints | Ask / Stop | Example |
| --- | --- | --- | --- | --- | --- |
| 0. Classify | User request | One task type | Do not handle unrelated side tasks | If intent changes data but source is unclear, ask | "查 POI" -> `query` |
| 1. Locate | Current environment | Wiki root path | Prefer `~/.codex/skills/wiki-skill`, then repo `wiki-skill/` | Stop if `wiki.py` or `data/terms.json` is missing | `cd ~/.codex/skills/wiki-skill` |
| 2. Inspect | Task type and known context | Scenario/tag/source plan | Read `scenarios` before inventing categories | Ask if scenario choice affects meaning | `python3 wiki.py scenarios` |
| 3. Retrieve / Dedupe | Keyword, scenario, industry, tag | Matches, empty result, or conflict | Query before add/import | Stop on duplicate names or conflicting definitions | `python3 wiki.py query -k POI -f json` |
| 4. Decide / Write | Source facts and target schema | CLI add command or JSON edit plan | Source, definition, scenario required;机审类 requires `premise` | Ask if source/boundary/validity is missing | `add --source-type user --validity pending` |
| 5. Validate | Changed files | Validation evidence | Every data change must run validation | If validation fails, read errors before editing | `python3 wiki.py validate` |
| 6. Deliver | Query/write/validation evidence | Final concise handoff | Mention source validity and residual risk | Do not claim completion without evidence | "Added 3 terms; validate passed" |

## Business-Flow Summary Contract

Use this when the task type is `business-flow` or when adding/importing terms from a process document.

### Required Inputs

- `business_domain`: e.g. 抖音生活服务, 机审运营, 电商商品, 内容安全.
- `scenario`: one or more registered scenarios from `data/scenarios.json`.
- `source_material`: user document, existing wiki term, rule text, web source, or explicit user statement.
- `terms`: names, aliases, labels, metrics, roles, tools, or actions involved.
- `decision_goal`: what the flow is used to decide, detect, explain, or generate.

### Required Output Shape

```markdown
## 业务流：<name>

- 输入：<facts, documents, signals, user request, source fields>
- 处理：<ordered steps or transformation logic>
- 输出：<labels, definitions, prompt fragments, decisions, reports>
- 约束：<source priority, scenario boundary, validity, required premise>
- 风险：<ambiguity, missing source, conflicting term, pending validity>
- 校验：<query/validate commands or manual coverage checks>
```

### Flow Levels

Use the lowest sufficient level:

1. **Term level**: one term and its aliases, definition, premise, scenarios.
2. **Scenario level**: all terms under one business scenario, such as `生活服务` or `机审场景`.
3. **Chain level**: an end-to-end process, such as `POI -> 到店 -> 团购 -> 核销 -> 有效核销GMV`.
4. **Prompt level**: a compact block meant to be embedded into another agent's system prompt.

Do not jump to chain level if the user only asked for one term.

## Query Rules

1. Prefer scoped lookup:
   - exact keyword first: `python3 wiki.py query -k <term> -f json`
   - then scenario: `python3 wiki.py query -s <scenario> -f prompt`
   - then industry/tag when helpful: `-i <industry>` or `-t <tag>`
2. Return source and validity when the answer affects business rules or PE behavior.
3. If multiple entries match, separate them by scenario and premise.
4. If no entry matches, say the term is missing and propose `add-term` only if the user wants it.

## Prompt-Fragment Rules

For PE or system prompt material, use `-f prompt` and keep output compact.

Required checks:

- Include only relevant terms.
- Preserve premises and boundaries.
- Mark `pending` entries if they appear in the prompt material.
- Do not include raw JSON unless requested.

Example:

```bash
python3 wiki.py query -s 机审场景 -f prompt
python3 wiki.py query -s 流量场景 -t 流量分层 -f prompt
```

## Add-Term Rules

Use CLI `add` for simple entries.

Required fields:

- `--name`
- `--definition`
- `--scenarios`
- `--source` or explicit source text
- `--source-type`
- `--validity`

Recommended fields:

- `--aliases`
- `--industries`
- `--tags`
- `--premise`

Validity rules:

- `verified`: only when source is user-provided authoritative material, internal material, or a verified official/primary source.
- `pending`: public web source, uncertain business meaning, or no internal confirmation.
- `deprecated`: term kept for compatibility but no longer current.

For web terms that are not official/internal, put this in `premise` if `meta.source_note` cannot be set through CLI:

```text
公开来源口径，未核验为官方或内部统一标准；如内部文档另有定义，以内部口径为准。
```

## Import-Terms Rules

Use this when the user provides a dictionary, rule document, markdown file, spreadsheet, or list.

### Required Import Steps

1. Read the source structure.
2. Extract candidate main terms, aliases, subterms, labels, metrics, tools, roles, and actions.
3. Query existing wiki names and aliases before adding.
4. Map each term to registered `scenarios`; add new scenario only when existing scenarios are insufficient.
5. Bind `industries` and `tags` when the source gives business context.
6. Put rules, thresholds, formulas, exemptions, and applicability boundaries into `premise`.
7. Preserve source path or URL in `meta.source`.
8. Run coverage check against source headings or source rows.
9. Run validation.

### Import Output

Report:

- Number of added terms.
- Number of skipped duplicate terms.
- New scenarios, if any.
- Source path or URL.
- Coverage check result.
- Validation command and result.

## Validation Rules

Run after every data edit:

```bash
python3 wiki.py validate
python3 /Users/zhangfeng/.codex/skills/.system/skill-creator/scripts/quick_validate.py <wiki-skill目录>
```

For imports, also run a coverage check against the source document headings, rows, or explicit term list.

Validation failure handling:

1. Read the exact failing term and field.
2. Fix the smallest schema or duplicate issue.
3. Re-run validation.
4. Do not reformat unrelated data.

## Stop Conditions

Stop and ask the user when:

- The term meaning changes label semantics or audit boundary and no authoritative source exists.
- The source document conflicts with existing verified wiki entries.
- A required scenario is ambiguous and picking one would alter retrieval behavior.
- The user asks to publish/sync but the target repo or destination path is unclear.
- Files are outside writable scope and write approval is denied.

## Final Handoff Template

```markdown
改动/结果：
- <what changed or what was found>

使用的文件/命令：
- `<command or file>`

数据有效性：
- source_type=<web|user|internal>, validity=<verified|pending|deprecated>

验证：
- `<command>` -> <result>

未覆盖风险：
- <none or explicit risk>
```

## Small-Model Checklist

Before final response, verify these are true:

- I selected one task type.
- I used the wiki root that contains `wiki.py`.
- I checked scenarios before adding a new one.
- I queried before adding or importing.
- I did not mark unsourced terms as `verified`.
- I preserved source and premise for business rules.
- I ran validation after edits.
- I reported remaining uncertainty instead of hiding it.
