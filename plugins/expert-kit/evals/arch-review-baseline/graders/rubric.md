# Architecture Review Grader Rubric

Score the response on the following binary criteria (1 point each, pass threshold >= 4/5):

1. **Hooks Collision Detection**: Identifies that placing `hooks/hooks.json` alongside root `plugin.json` is ignored/warned by Antigravity CLI (which reads root `hooks.json` only) and recommends isolating Claude hooks via `.claude-plugin/hooks.json`.
2. **Unquoted Path Detection**: Flags unquoted `${CLAUDE_PLUGIN_ROOT}/run.sh` as a P0/P1 portability/injection defect and recommends quoting or exec-form `args`.
3. **YAML Type Mismatch Detection**: Identifies that `tools: Read, Grep, Glob` (string) causes Antigravity's strict YAML parser to fail and skip the agent (expects list or portable frontmatter).
4. **Context Budget Detection**: Flags the 32 KB `rules/AGENTS.md` as exceeding the 24 KB per-file truncation limit and recommends offloading reference docs to `skills/<name>/references/`.
5. **Actionable Prioritization**: Ranks findings by severity (`P0`/`P1`/`P2`) with concrete remediation steps and verification commands.
