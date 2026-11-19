# Writing Kit

**Writing Kit** is a cross-CLI expert writing plugin engineered for **Claude Code**, **Codex CLI**, and **Antigravity CLI** from a single canonical specification (`spec/*.json`). Built on cognitive writing theory, classical rhetoric, editorial journalism, and Korean prose craft, it transforms AI writing from generic knowledge-telling into disciplined, author-owned knowledge-crafting.

## Key Capabilities

- **World-Class Writing Skill (`skills/world-class-writing`)**: Progressive-disclosure workflow grounded in an 8-dimension expert competency rubric (**W1–W8**), 3-tier adaptive rigor (`Light` / `Standard` / `Flagship`), an adaptive 3-question elicitation gate, and four on-demand genre profiles (`technical`, `executive`, `essay`, `persuasive`).
- **Deterministic Korean & English Prose Auditor (`scripts/prose_audit.py`)**: Zero-dependency Python 3.9+ diagnostics engine detecting Korean double passives, translationese, nominalization, `의`-chaining, end-stop monotony, bilingual AI slop, and sentence burstiness (CV). Supports `--compare` v1-to-v2 deltas while masking code blocks, quotes, frontmatter, and URLs.
- **Independent Adversarial Editor (`agents/editorial-critic.md`, `com.openai/agents/editorial-critic.toml`)**: Read-only specialist subagent enforcing zero flattery, three P0 hard gates, a 10–15% deletion budget, steelman counter-argument stress-testing, and evidence-anchored W1–W8 scorecards.
- **Behavioral Evals (`evals/`)**: Three pressure-tested L3 evaluation suites covering Korean executive memos, technical RFC critiques, and anti-slop essays.

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

## Quick Usage (`prose_audit.py`)

```bash
# Audit a single draft with genre calibration (technical | executive | essay | persuasive | general)
python3 skills/world-class-writing/scripts/prose_audit.py draft.md --genre executive

# Compare draft v1 against revised v2 to verify measurable reduction in slop/defects
python3 skills/world-class-writing/scripts/prose_audit.py --compare draft_v1.md final_v2.md --genre essay --strict
```

## Verification

Run self-diagnostics and deterministic auditor unit tests directly with Python 3 (zero external dependencies):

```bash
python3 core/doctor.py --ci
python3 -m unittest discover -s tests -p "test_*.py"
```
