# Expert Kit

Expert Kit adds a 7-dimension architecture review skill, deterministic shell and stop hooks, a stdio MCP diagnostics server, and a read-only `arch-reviewer` subagent to **Claude Code**, **Codex CLI**, and **Antigravity CLI**. All runtime scripts require Python 3.9+ and zero third-party packages.

## Components

| Component | Path | Purpose |
| :--- | :--- | :--- |
| **Architecture Review Skill** | `skills/architecture-review/` | Progressive-disclosure workflow grounded in the D1–D7 Principal Engineering Rubric, structured output example, and `scripts/context_audit.py`. |
| **Engineering Invariants** | `rules/AGENTS.md` | Always-on rules (< 2,000 tokens, strictly under 24 KB) covering SSOT, deterministic guardrails, context budgets, and command verification. |
| **Universal Hook Adapter** | `core/hooks/` | Python 3.9+ stdlib dispatcher running `safety_guard`, `quality_gate`, and `session_context` policies across Antigravity, Claude Code, and Codex CLI. |
| **Diagnostics MCP Server** | `core/mcp/server.py` | Zero-dependency JSON-RPC 2.0 stdio server exposing `plugin_diagnostics` and `check_context_budget`. |
| **Read-Only Subagent** | `agents/arch-reviewer.md`, `com.openai/agents/arch-reviewer.toml` | Independent architecture reviewer with `read` and `search` capabilities compiled from `spec/agents/arch-reviewer.json`. |
| **Behavioral Eval** | `evals/arch-review-baseline/` | Opt-in L3 evaluation suite covering baseline architecture review rigor. |

## Installation

### Claude Code
```text
/plugin install expert-kit --marketplace taepyeong-build/universal-plugin
```

### Codex CLI
```bash
codex plugin marketplace add https://github.com/taepyeong-build/universal-plugin
codex plugin add expert-kit@universal-plugins
```

Codex installs the skill, rules, and `arch-reviewer` subagent directly. To enable hooks in a Codex workspace, adopt `com.openai/hooks.json` explicitly.

### Antigravity CLI
```bash
agy plugin install https://github.com/taepyeong-build/universal-plugin/tree/main/plugins/expert-kit
```

## Usage and Configuration

### Architecture Review and Context Budget Audit

Invoke the `architecture-review` skill (or delegate to `arch-reviewer`) when auditing system invariants, failure modes, or plugin structure. To check `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` (24,000-byte cap), and `SKILL.md` (500-line cap) directly from the terminal:

```bash
cd plugins/expert-kit
python3 skills/architecture-review/scripts/context_audit.py /path/to/target-repo
```

### Hook Policies and Runtime Detection

The Universal Hook Adapter detects Antigravity from `camelCase` payload keys (`hookEventName`, `toolCall`, `continuationActive`, `conversationId`). Claude Code and Codex CLI share `snake_case` payloads; the adapter selects `codex` when `EXPERT_KIT_RUNTIME=codex`, `CODEX_HOME`, `CODEX_SANDBOX`, or `CODEX_THREAD_ID` is set, and defaults to `claude`.

| Policy | Event | Behavior |
| :--- | :--- | :--- |
| **`safety_guard`** | `tool.before` (`shell.exec`) | Denies root/home `rm -rf`, `/dev/` `mkfs`/`dd` writes, fork bombs, force-push to `main`/`master`, and `curl`/`wget` piped to a shell. Prompts on `git reset --hard`, `git clean -f`, and `chmod 777`. |
| **`quality_gate`** | `turn.stop` | Inactive (`allow`) unless `EXPERT_KIT_STOP_CHECK_CMD` is set. Runs the command (10s timeout), blocks stopping once on non-zero exit or timeout, and honors `continuationActive` / `stop_hook_active` to prevent recursive loops. |
| **`session_context`** | `session.start` | Injects a concise `rules/AGENTS.md` pointer for Claude Code and Codex CLI; skipped on Antigravity, which loads `rules/AGENTS.md` natively. |

Enable the optional Stop quality gate in your shell environment:

```bash
export EXPERT_KIT_STOP_CHECK_CMD="python3 -m unittest discover -s tests"
```

Hook events log as JSONL to `${PLUGIN_DATA}/logs/hooks.jsonl` (fallback: `~/.cache/expert-kit/logs/hooks.jsonl`). MCP tool calls log to `${EXPERT_KIT_DATA}/logs/mcp.jsonl` (fallback: `${PLUGIN_DATA}` or `${CLAUDE_PLUGIN_DATA}`).

## Verification

Run the health check and contract tests from `plugins/expert-kit` with Python 3.9+ (zero third-party packages):

```bash
cd plugins/expert-kit
python3 core/doctor.py --ci
python3 -m unittest discover -s tests -p "test_*.py"
```
