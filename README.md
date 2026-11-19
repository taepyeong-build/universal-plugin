# Universal Expert Plugins Monorepo

A zero-dependency, single-source-of-truth (SSOT) plugin platform compatible with **Claude Code**, **Codex CLI**, and **Antigravity CLI** (`claude`, `codex`, `agy`).

## Architecture Decisions (ADR-01 ~ ADR-05)

1. **Multi-Plugin Monorepo + 3 Marketplaces**: Manage all plugins under `plugins/<name>/` and generate `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`, and `marketplace.json` from `registry.json`.
2. **Zero-Collision Polyglot Bundles**: Each `plugins/<name>/` directory is directly installable across all 3 CLIs with zero strict-mode warnings (`hooks.json` for AGY, `.claude-plugin/hooks.json` for Claude, `com.openai/` for Codex).
3. **Full-Stack 5-Component Modular Opt-In**: Supports `Skills`, `Rules`, `Hooks`, `MCP`, and `Subagents`; `tools/sync.py` generates adapters strictly for components declared under `spec/`.
4. **Python 3.9+ Stdlib Zero-Dependency Runtime**: Canonical `spec/*.json` + JSON Schema (`schemas/`), zero `pip`/`npm` install steps, fast deterministic hooks, and built-in stdio MCP.
5. **3-Layer Verification Gate**:
   - **L1**: `sync.py --check` + `agy plugin validate --strict` + `claude plugin validate --strict --profile directory` + isolated `CODEX_HOME` install test.
   - **L2**: Stdlib `unittest` contract suites (3-dialect hooks, stop anti-loop, MCP JSON-RPC) + `doctor.py --ci`.
   - **L3**: Opt-in behavioral A/B evals (`evals/`, run via `--with-evals`).

## Quick Start

```bash
# 1. Regenerate all adapters & 3 marketplace catalogs from SSOT
python3 tools/sync.py

# 2. Run L1 + L2 verification across all 3 CLIs
python3 tools/verify.py

# 3. Scaffold a new plugin (modular opt-in)
python3 tools/new_plugin.py my-plugin --description "Custom workflow plugin" --with-hooks --with-mcp

# 4. Run L3 behavioral evals when ready
python3 tools/verify.py --with-evals
```

## Repository & Installation

- **Canonical Repository**: `https://github.com/taepyeong-build/universal-plugin`

```bash
# Claude Code
/plugin install expert-kit --marketplace taepyeong-build/universal-plugin

# Codex CLI
codex plugin marketplace add https://github.com/taepyeong-build/universal-plugin
codex plugin add expert-kit@universal-plugins

# Antigravity CLI
agy plugin install https://github.com/taepyeong-build/universal-plugin/tree/main/plugins/expert-kit
```
