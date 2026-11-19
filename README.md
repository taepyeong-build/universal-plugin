# Universal Expert Plugins

> [한국어 요약 안내 (README.ko.md)](./README.ko.md)

This monorepo builds and verifies zero-dependency agent plugins for **Claude Code**, **Codex CLI**, and **Antigravity CLI** (`claude`, `codex`, `agy`) from a single canonical specification. Every runtime script requires Python 3.9+ and zero third-party packages.

## Plugins

| Plugin | Version | Category | Components | Summary |
| :--- | :---: | :--- | :--- | :--- |
| [`expert-kit`](./plugins/expert-kit/README.md) | `1.0.0` | Developer Tools | Skills, Rules, Hooks, MCP, Subagent, Scripts, Evals (1) | 7-dimension architecture review (`architecture-review`), shell and stop hooks, stdio context-budget MCP server, and read-only `arch-reviewer`. |
| [`writing-kit`](./plugins/writing-kit/README.md) | `1.0.0` | Productivity | Skills, Rules, Subagent, Scripts, Evals (3) | W1–W8 writing workflow (`world-class-writing`), 4 on-demand genre profiles, Korean/English `prose_audit.py`, and read-only `editorial-critic`. |

## Install a Plugin

### Claude Code
```text
/plugin install expert-kit --marketplace taepyeong-build/universal-plugin
/plugin install writing-kit --marketplace taepyeong-build/universal-plugin
```

### Codex CLI
```bash
codex plugin marketplace add https://github.com/taepyeong-build/universal-plugin
codex plugin add expert-kit@universal-plugins
codex plugin add writing-kit@universal-plugins
```

Codex installs plugin skills, rules, and subagents directly. Workspace hooks under `com.openai/hooks.json` remain an opt-in template.

### Antigravity CLI
```bash
agy plugin install https://github.com/taepyeong-build/universal-plugin/tree/main/plugins/expert-kit
agy plugin install https://github.com/taepyeong-build/universal-plugin/tree/main/plugins/writing-kit
```

## Develop and Verify Plugins

Requires **Python 3.9+**. Running `python3 tools/verify.py` also requires `claude`, `codex`, and `agy` on `PATH` (missing any CLI fails L1 validation). Passing `--with-evals` runs L3 behavioral evals through `claude` and spends LLM tokens.

```bash
# 1. Regenerate per-CLI adapters and 3 marketplace catalogs from SSOT specs
python3 tools/sync.py

# 2. Run L1 (3-CLI strict validation) and L2 (unit tests + doctor --ci)
python3 tools/verify.py

# 3. Scaffold a new plugin (core skills/rules + optional hooks, MCP, agents, evals)
python3 tools/new_plugin.py my-plugin --description "Custom workflow plugin." --with-hooks --with-mcp

# 4. Run opt-in L3 behavioral evals (requires claude CLI)
python3 tools/verify.py --with-evals
```

## Architecture and Trade-Offs

| Area | Design | Trade-Off / Boundary |
| :--- | :--- | :--- |
| **SSOT compilation** | `tools/sync.py` compiles `registry.json` and `plugins/*/spec/*.json` into 3 marketplace catalogs and per-CLI adapters for opt-in `hooks`, `mcp`, and `agents`. `skills/` and `rules/` ship directly without a build step. | Contributors must re-run `tools/sync.py` after spec edits; `tools/sync.py --check` blocks drift in verification. |
| **Zero-collision layout** | Each CLI reads an isolated adapter path (`hooks.json` for Antigravity, `.claude-plugin/hooks.json` for Claude Code, `com.openai/hooks.json` for Codex) inside `plugins/<name>/`. | Codex workspace hooks do not auto-activate on plugin install; users adopt `com.openai/hooks.json` explicitly. |
| **Stdlib-only runtime** | Hooks, `doctor.py`, MCP servers, and `prose_audit.py` run on Python 3.9+ stdlib with no `pip` or `npm` install step. | Files under `schemas/` guide IDE authoring via `$schema` rather than full draft-2020-12 runtime validation. |
| **3-layer verification** | `tools/verify.py` runs L1 (SSOT drift + 3-CLI validators/install) and L2 (`unittest` contract suites + `doctor.py --ci`) on every run. | L3 behavioral evals (`evals/`) stay opt-in via `--with-evals` to keep routine checks deterministic and free of LLM cost. |
