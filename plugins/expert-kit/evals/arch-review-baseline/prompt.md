Review the plugin directory layout below and identify the top architectural risks across Claude Code, Codex CLI, and Antigravity CLI compatibility:

- `plugin.json` (Agent Plugins 1.0.0 schema)
- `hooks/hooks.json` (containing unquoted `${CLAUDE_PLUGIN_ROOT}/run.sh`)
- `agents/reviewer.md` (with frontmatter `tools: Read, Grep, Glob`)
- `rules/AGENTS.md` (32 KB file containing full API documentation)

Provide severity-ranked findings (`P0`/`P1`/`P2`) with exact failure modes and concrete fixes.
