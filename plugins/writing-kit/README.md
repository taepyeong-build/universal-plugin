# Writing Kit

Writing Kit adds a rubric-driven Korean and English writing workflow, a deterministic `prose_audit.py` linter, and a read-only `editorial-critic` subagent to **Claude Code**, **Codex CLI**, and **Antigravity CLI**. It runs on Python 3.9+ with zero third-party packages.

## Components

| Component | Path | Purpose |
| :--- | :--- | :--- |
| **Writing Workflow Skill** | `skills/world-class-writing/` | 8-dimension competency rubric (W1–W8), 4 modes (`Draft`, `Rewrite`, `Critique`, `Outline`), 3 rigor tiers (`Light`, `Standard`, `Flagship`), max-3-question elicitation gate, and 4 on-demand genre profiles (`technical`, `executive`, `essay`, `persuasive`). |
| **Editorial Invariants** | `rules/AGENTS.md` | Always-on rules (< 2 KB) enforcing zero fabricated metrics, author ownership, anti-slop discipline, and single-genre loading. |
| **Deterministic Prose Auditor** | `skills/world-class-writing/scripts/prose_audit.py` | Python 3.9+ stdlib diagnostics engine detecting Korean double passives, translationese, nominalization, `의`-chaining, 3+/5+ identical-ending runs, bilingual AI slop, hedge density, generic headings, and sentence burstiness (CV). |
| **Adversarial Editorial Critic** | `agents/editorial-critic.md`, `com.openai/agents/editorial-critic.toml` | Read-only subagent enforcing zero flattery, 3 P0 hard gates, a 10–15% deletion budget, steelman counter-arguments, and evidence-anchored W1–W8 scorecards. |
| **Behavioral Evals** | `evals/` | Three opt-in L3 evaluation suites covering Korean executive memos, technical RFC critiques, and anti-slop essays. |

## Installation

### Claude Code
```text
/plugin install writing-kit --marketplace taepyeong-build/universal-plugin
```

### Codex CLI
```bash
codex plugin marketplace add https://github.com/taepyeong-build/universal-plugin
codex plugin add writing-kit@universal-plugins
```

### Antigravity CLI
```bash
agy plugin install https://github.com/taepyeong-build/universal-plugin/tree/main/plugins/writing-kit
```

## Usage

### Writing Workflow and Editorial Critic

Invoke the `world-class-writing` skill when drafting, rewriting, critiquing, or outlining substantial Korean or English prose. Pass `--light`, `--standard`, or `--flagship` to override the automatic rigor tier; `Flagship` tasks and `Mode C` critiques automatically delegate independent review to `editorial-critic`.

### Deterministic Prose Auditor (`prose_audit.py`)

Run `prose_audit.py` directly from `plugins/writing-kit` (or from an installed plugin root) to audit a file, read from stdin, or verify v1-to-v2 revision deltas:

```bash
cd plugins/writing-kit

# Audit a draft with genre calibration (technical | executive | essay | persuasive | general)
python3 skills/world-class-writing/scripts/prose_audit.py draft.md --genre executive

# Audit prose piped via stdin
cat draft.md | python3 skills/world-class-writing/scripts/prose_audit.py --stdin --genre technical

# Compare v1 against revised v2 and fail on warnings (--strict)
python3 skills/world-class-writing/scripts/prose_audit.py --compare draft_v1.md final_v2.md --genre essay --strict
```

Before scanning, `prose_audit.py` masks YAML frontmatter, fenced and inline code, Markdown blockquotes (`>`), HTML comments, table rows, and URLs. Exit codes: `0` pass, `1` P0 error (or any warning under `--strict`), `2` file or CLI error.

## Verification

Run the doctor and unit tests from `plugins/writing-kit` (Python 3.9+):

```bash
cd plugins/writing-kit
python3 core/doctor.py --ci
python3 -m unittest discover -s tests -p "test_*.py"
```
