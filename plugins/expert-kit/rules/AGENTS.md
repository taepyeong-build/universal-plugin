# Expert Kit Engineering Invariants

These rules stay concise (< 2,000 tokens, strictly under the 24 KB per-file cap) and define non-negotiable engineering invariants across Claude Code, Codex CLI, and Antigravity CLI.

## 1. Single Source of Truth (SSOT)
- Never hand-edit generated adapter files (`plugin.json`, `.claude-plugin/*`, `hooks.json`, `mcp*.json`, `.mcp.json`, `com.openai/*`, `agents/*.md`, or root marketplaces) when a `spec/` source exists.
- Edit `spec/*.json` or `registry.json` and run `python3 tools/sync.py` followed by `python3 tools/verify.py`.

## 2. Deterministic Control Over Prompt Persuasion
- Enforce hard safety invariants (destructive shell commands, secret leaks, stop-loop boundaries) in deterministic hooks or typed MCP tools rather than relying on prose alone.
- Keep hook handlers fast (< 200 ms) and side-effect free on `stdout`; emit diagnostics only to `${PLUGIN_DATA}/logs/`.

## 3. Context Economics (Progressive Disclosure)
- Keep always-on rules minimal and high-signal.
- Keep `SKILL.md` under 500 lines; offload checklists, schemas, and examples into `references/` and `examples/`.
- Prefer running deterministic scripts in `scripts/` over pasting verbose raw manuals into context.

## 4. Verification Before Completion
- Never claim a change is verified without executing the concrete command or test suite and inspecting its exit status and output.
