# 7-Dimension Principal Competency Rubric

Use this reference to score architecture decisions and plugin designs consistently.

| Dimension | Failing (Anti-Pattern) | Principal Standard (Target) |
| :--- | :--- | :--- |
| **D1. SSOT & Standards** | Copy-pasted configs per tool; manual drift between manifests | Open standards core + generated adapters + `--check` drift gate |
| **D2. Context Economics** | Monolithic 2,000-line rules loaded every turn | Rules < 2,000 tokens (<= 24 KB); `SKILL.md` < 500 lines; `references/` on-demand |
| **D3. Control vs. Reasoning** | Asking LLM prose to "please never run rm -rf" | Deterministic `PreToolUse` / `Stop` hooks + typed MCP tools; anti-loop guards |
| **D4. Fault Isolation & Security** | Unquoted paths, hardcoded secrets, single MCP failure kills plugin | Independent failure isolation; quoted paths; `ROOT` vs `DATA` separation |
| **D5. Verification & Evals** | "Looks right" without tests or baseline comparison | Multi-CLI `--strict` + contract unit tests + A/B behavioral evals |
| **D6. Lifecycle Governance** | Breaking schema flips without fallback or SemVer discipline | Dual-mode transition configs, synchronized SemVer, multi-marketplace catalogs |
| **D7. Observability & DX** | `print()` debugging polluting JSON stdout; opaque failures | Structured JSONL logs in `${PLUGIN_DATA}/logs/` + sub-5s `doctor` self-check |
