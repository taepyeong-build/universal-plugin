---
name: architecture-review
description: >-
  Use when conducting a principal-level architecture review, auditing cross-CLI
  agent plugins, evaluating system modularity and failure modes, or checking
  context budgets and deterministic guardrails.
---

# Principal Architecture Review

Execute an evidence-based architecture review anchored on the 7-dimension Principal Engineering Rubric.

## Workflow

1. **Scope & Invariant Discovery**
   - Identify the system boundaries, single source of truth (SSOT), external interfaces, and trust boundaries.
   - Read only the files needed for the review scope to preserve context budget.

2. **Deterministic Audit First**
   - Run the bundled context budget audit script against the target directory:
     ```bash
     python3 ./scripts/context_audit.py <target-dir>
     ```
   - Inspect existing automated validation, schema checks, and unit tests before forming opinions.

3. **7-Dimension Rubric Evaluation**
   - Consult [competency-rubric.md](./references/competency-rubric.md) only when scoring detailed trade-offs across:
     - D1: Standards & SSOT
     - D2: Context Economics & Progressive Disclosure
     - D3: Deterministic Control vs. Stochastic Reasoning
     - D4: Fault Isolation, Portability & Zero-Trust Security
     - D5: Verification & Behavioral Evals
     - D6: Lifecycle Governance & Compatibility
     - D7: Observability & DX

4. **Produce Structured Findings**
   - Format the final review following [review-output.md](./examples/review-output.md).
   - Every finding MUST include: Severity (`P0`/`P1`/`P2`), exact file path + line evidence, concrete failure mode, and smallest safe fix.

## Verification Checklist
- [ ] Every cited path and behavior was directly inspected (no assumptions).
- [ ] Deterministic audit script or test results are included as evidence.
- [ ] Recommendations distinguish must-fix blockers (`P0`) from optional follow-ups (`P2`).
