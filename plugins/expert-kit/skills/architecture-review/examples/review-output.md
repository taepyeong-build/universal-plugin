# Example Architecture Review Output

## Executive Verdict
- **Status**: Needs Remediation (1 P0, 1 P1)
- **Deterministic Checks**: `context_audit.py` flagged `rules/AGENTS.md` at 28.4 KB (exceeds 24 KB cap).

## Findings

### [P0] Unquoted Plugin Root Path in Hook Command
- **Evidence**: `.claude-plugin/hooks.json:9`
- **Failure Mode**: Installation paths containing spaces split the shell invocation into invalid arguments and fail silently or execute unintended tokens.
- **Remediation**: Quote `"${CLAUDE_PLUGIN_ROOT}/core/hooks/dispatch.py"` or use exec-form `args`.

### [P1] Always-On Rule Exceeds 24 KB File Budget
- **Evidence**: `rules/AGENTS.md` (28,410 bytes)
- **Failure Mode**: Antigravity truncates files over 24,000 bytes at line boundaries, silently dropping bottom invariants.
- **Remediation**: Move detailed examples into `skills/<name>/references/` and reduce `rules/AGENTS.md` below 8 KB.

## Verification Commands
```bash
python3 tools/sync.py --check
python3 tools/verify.py
```
