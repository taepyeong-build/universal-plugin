# Expert Kit

**Expert Kit** is a cross-CLI reference plugin engineered for **Claude Code**, **Codex CLI**, and **Antigravity CLI** from a single canonical specification (`spec/*.json`). It bundles principal-level architecture review workflows, a zero-dependency Universal Hook Protocol Adapter for deterministic safety and stop-loop guardrails, a standard stdio Model Context Protocol (MCP) diagnostics server, concise always-on engineering invariants, and portable review subagents.

## Key Capabilities

- **Architecture Review Skill (`skills/architecture-review`)**: Progressive-disclosure workflow with a 7-dimension Principal Engineering Rubric, structured output examples, and a deterministic context-budget audit script.
- **Universal Hook Adapter (`core/hooks/`)**: Single Python 3 standard-library runtime that auto-detects Antigravity (`camelCase`), Claude Code (`snake_case`), and Codex CLI payloads, runs deterministic safety and stop-loop policies, and logs structured JSONL diagnostics exclusively to persistent plugin data storage.
- **Diagnostics MCP Server (`core/mcp/server.py`)**: Zero-dependency JSON-RPC 2.0 stdio server exposing `plugin_diagnostics` and `check_context_budget` tools.
- **Portable Subagent (`agents/arch-reviewer.md`, `com.openai/agents/arch-reviewer.toml`)**: Read-only architecture reviewer synthesized from a single capability profile.

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

### Antigravity CLI
```bash
agy plugin install https://github.com/taepyeong-build/universal-plugin/tree/main/plugins/expert-kit
```

## Verification

Run the bundled health and contract checks directly with Python 3 (no external packages required):

```bash
python3 core/doctor.py --ci
python3 -m unittest discover -s tests -p "test_*.py"
```
