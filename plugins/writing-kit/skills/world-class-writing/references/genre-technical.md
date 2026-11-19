# Genre Profile: Technical & Engineering Writing (`technical`)

**Target Documents**: RFCs, ADRs (Architecture Decision Records), System Design Docs, API/SDK Guides, Postmortems, Staff+ Engineering Blogs.
**Starred Dimensions (must be `>= 2` each)**: **W2 (Epistemic Rigor) ★, W3 (Information Architecture) ★, W5 (Signal Density) ★**.

---

## 1. Structural Architecture

### A. Decision Documents (RFC / ADR / Design Doc)
Follow the Staff+ decision spine in order — never bury the trade-offs:
1. **Context & Concrete Problem**: Exact failure mode, bottleneck, or invariant at risk (include reproducible metric or incident scope).
2. **Non-Goals & Constraints**: Explicitly declare what this proposal will NOT solve (prevents scope creep and reader confusion).
3. **Options Considered (including "Do Nothing")**: Compare `>= 2` serious alternatives fairly; include latency, complexity, migration cost, and operational blast radius.
4. **Proposed Decision & Mechanism**: Precise architecture, data flow, interface contract, and failure-handling semantics.
5. **Trade-Offs, Risks & Rollback Plan**: Name the exact cost accepted by this choice, how failure will be detected, and how to revert safely.
6. **Verification Plan**: Deterministic tests, canary criteria, or measurable success thresholds.

### B. Documentation & Guides (Diátaxis 4-Quadrant Discipline)
Never mix two Diátaxis quadrants in one page:
- **Tutorial** (Learning-oriented): Safe, repeatable guided step sequence; explain minimal theory.
- **How-To Guide** (Task-oriented): Assumes competence; solves one real operational problem directly.
- **Reference** (Information-oriented): Dry, accurate, consistent schema/API specification; zero opinion.
- **Explanation** (Understanding-oriented): Clarifies "why" and architectural trade-offs; no step-by-step recipe.

### C. Engineering Postmortems & Tech Blogs
- **Postmortem**: Blameless timeline (UTC/KST timestamps) → Root Cause (5 Whys / contributing factors) → Blast Radius → Action Items with owners & deadlines.
- **Staff+ Tech Blog**: Open with the surprising failure or hard constraint → show the rejected naive fix → walk through the exact mechanism with real code/traces → state boundary conditions where your solution does NOT apply.

---

## 2. Genre-Specific Editorial Rules

1. **Zero Weasel Words**: Ban `빠르게`, `확장 가능하게`, `안전하게`, `significantly faster`, `very reliable` without bounded numbers or mechanisms (`p99 < 40 ms`, `10k RPS under 4 vCPU`).
2. **Code-to-Prose Alignment**: Every code block or config snippet must be minimal, runnable or syntactically valid, and immediately precede or follow the exact invariant it illustrates.
3. **Explicit Invariants & Edge Cases**: Specify what happens on timeout, partial failure, retry, null/empty input, and backward compatibility.
4. **Terminology Stability**: Pick one exact term per concept (`plugin root`, `워크스페이스`) and never swap synonyms for stylistic variety.

---

## 3. Audit Calibration (`--genre technical`)

- Structured tables, code blocks, and concise checklists are **encouraged** (no bold-bullet penalty).
- **Strict checks**: Zero fabricated benchmarks (`[확인 필요: 벤치마크 수치]`), low hedge/weasel density, high concrete-anchor density (numbers, units, symbols, commands), clean KO/EN technical terminology without double passives.
- **Thesis / Value Gate**:
  - RFC / ADR / Tech Blog → **Negation Test** (a Staff engineer could credibly prefer another option).
  - Reference / How-To / Runbook → **Reader Actionability Test** (reader can execute without guessing hidden prerequisites).
