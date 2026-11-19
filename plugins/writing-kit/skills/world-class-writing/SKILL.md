---
name: world-class-writing
description: >-
  Use when drafting, rewriting, editing, critiquing, or outlining high-stakes
  prose in Korean or English — including technical docs (RFC, ADR, design doc,
  tech blog), executive memos (6-pager, proposal, report), essays/articles, or
  persuasive copy — or when the user asks "글 써줘", "초안 다듬어줘",
  "AI투/번역투 없애줘", "논리 점검해줘", or "편집 비평해줘". Do NOT use for
  pure code edits, raw data extraction, or casual one-line chat replies.
---

# World-Class Writing Workflow

Transform writing from generic LLM knowledge-telling into author-owned knowledge-crafting grounded in the 8-Dimension World-Class Writing Competency Rubric (**W1–W8**).

## 1. Route Mode, Genre, and Rigor Tier

Before writing a single paragraph, classify the request across three axes:

| Axis | Options | Routing Rule |
| :--- | :--- | :--- |
| **Mode** | `A: Draft` / `B: Rewrite` / `C: Critique` / `D: Outline` | New piece → `A`; existing draft to elevate → `B`; feedback only → `C`; structure/argument workshop → `D`. |
| **Genre** | `technical` / `executive` / `essay` / `persuasive` / `general` | Load **at most ONE** matching `references/genre-*.md` file on demand. For unlisted domains (e.g., academic, UX copy), use `general` (core W1–W8 + mirror any user style sample). |
| **Rigor Tier** | `Light` / `Standard` / `Flagship` | `< ~500자` routine comms → `Light`; normal articles/reports/rewrites → `Standard` (default); high-stakes RFC/ADR, 6-Pager, published essays, critical proposals → `Flagship`. Honor explicit user overrides (`--light`, `--standard`, `--flagship`). |

## 2. Adaptive Elicitation Gate (Author Ownership)

In `Mode A` and `Mode D` (`Standard` / `Flagship`), inspect the user's input for three essential author inputs:
1. **Audience & Shift**: Who is reading, what do they currently believe, and what decision or mental-model shift must follow?
2. **Falsifiable Core Thesis**: What single claim or recommendation anchors the piece (must pass the Negation Test; for pure reference/how-to docs, must pass the Reader Actionability Test)?
3. **Authentic Evidence & Constraints**: What real facts, numbers, failures, mechanisms, or non-negotiable constraints belong to the author?

- **Missing inputs**: Ask **only** for what is missing — **maximum 3 concise questions** in one turn.
- **Skip condition**: If the user already supplied rich notes/drafts, chose `Light` tier, or explicitly asked to draft immediately ("바로 써줘"), skip questions, declare explicit **Assumptions** at the top, and insert `[확인 필요: 구체 지표/근거]` wherever real data is absent. Never fabricate facts.

## 3. Execute Mode Workflow

### Mode A (Draft) & Mode D (Outline)
1. **Load Single Genre Profile**: Read ONLY the matching file from the Reference Map below.
2. **Build Assertion Skeleton**: Draft section headings as concrete claims or reader actions (never vague labels like `서론`, `본론`, `결론`, `배경`). Identify the strongest counter-argument (Steelman) and where it will be addressed.
   - *Mode D stops here* after stress-testing the Toulmin argument chain (`Claim → Evidence → Warrant → Counter-Argument`).
3. **Write High-Density Draft v1**:
   - Open directly with the core conclusion, problem tension, or concrete scene — zero throat-clearing.
   - Alternate between principles and concrete anchors (numbers, mechanisms, code, named failure cases) along Hayakawa's Ladder of Abstraction.
   - Consult [ko-en-prose-craft.md](./references/ko-en-prose-craft.md) for Korean translationese, passive voice, rhythm, and AI-slop rules.
4. **Audit & Adversarially Edit** (Section 4) → **Revise & Verify Diff** (Section 5).

### Mode B (Rewrite) & Mode C (Critique)
1. **Deterministic Audit First**: Run `prose_audit.py` on the user's draft **before** forming subjective opinions.
2. **Diagnose Structure Before Sentences**: Check W1–W3 (Audience, Thesis/Evidence, Macro-Structure) first. Do not waste effort polishing sentences inside a broken argument.
3. **Adversarial Review**:
   - *Mode C* delegates to `editorial-critic` (or applies the full W1–W8 Scorecard + 4 Anti-Sycophancy Protocols) and stops without overwriting the draft.
   - *Mode B* executes surgical revision preserving the author's verified facts and voice, then proves improvement via `--compare`.

## 4. Deterministic Audit & Anti-Sycophancy Gate

For every substantial draft or revision (`>= 300 chars` KO or `>= 80 words` EN):

1. **Run Deterministic Prose Audit**:
   ```bash
   python3 ./scripts/prose_audit.py <draft.md> --genre <genre>
   ```
   (Or pipe via `--stdin` when working inline.)
2. **Enforce Three P0 Hard Gates (Zero Tolerance)**:
   - **Epistemic Honesty (W2)**: Zero invented numbers, quotes, or citations.
   - **Thesis Value (W1/W2)**: Passes Negation Test (or Reader Actionability Test for pure reference docs).
   - **Mechanical Floor (W6/W7)**: `prose_audit.py` exits `0` (zero Korean double passives, zero high-density AI slop, zero 5+ identical-ending runs, zero essay bold-bullet bloat).
3. **Tier-Linked Adversarial Review**:
   - **Tier 1 (`Light`)**: Verify the 3 P0 Hard Gates; run `prose_audit.py` if `>= 300 chars`.
   - **Tier 2 (`Standard`)**: Run the **4 Anti-Sycophancy Self-Audit Protocols** before Final v2:
     1. *Zero Flattery* — list the sharpest structural/prose defects first.
     2. *10–15% Deletion Budget* — identify specific lines to cut or compress without losing substance.
     3. *Steelman Counter-Argument* — state the smartest skeptic's best objection and patch any unaddressed gap.
     4. *Evidence-Anchored W1–W8 Check* — verify starred genre dimensions (★) each `>= 2` and total `>= 18/24`.
   - **Tier 3 (`Flagship`) & `Mode C`**: Delegate independent review to the read-only **`editorial-critic`** subagent, passing the draft, Writing Brief, and `prose_audit.py` JSON output. Resolve all `P0` (and high-impact `P1`) findings before sign-off.

## 5. Final Revision & Quantitative Diff Proof

After applying editorial cuts and fixes to produce Final v2 (`Standard` / `Flagship` in Mode A/B):

```bash
python3 ./scripts/prose_audit.py --compare <draft_v1.md> <final_v2.md> --genre <genre>
```

Confirm: `ok: true` on Final v2, zero `P0` defects, reduced slop/translationese/bloat, and no accidental loss of concrete evidence.

## Anti-Rationalization Discipline

| Tempting Rationalization | Mandatory Counter-Rule |
| :--- | :--- |
| "It is short, so I can skip `prose_audit.py`." | Run `prose_audit.py` on every piece `>= 300 chars` (`>= 80 words`). Short prose fails fastest from density and slop defects. |
| "Adding a quick percentage makes the argument stronger." | Never invent numbers or citations. Use `[확인 필요: ...]` — fabricated evidence is an automatic `P0` fail. |
| "Bold-lead bullets (`- **핵심:** ...`) look clean and readable." | Restrict bullets to true parallel lists/comparisons. In essays and 6-Pagers, bold-lead bullet spam is an AI-slop `P0` defect. |
| "The user worked hard on this draft, so I should praise it first." | Zero flattery in Mode B/C. Respect the author by surfacing structural flaws (`W1–W3`) before line edits. |
| "I already avoided slop mentally, so `--compare` is redundant." | LLMs miss their own repetition and nominalization drift. Always verify Final v2 with deterministic output. |

## On-Demand Reference Map (Progressive Disclosure)

Load **only** the files relevant to the current task:
- Scoring rubric & genre weights: [competency-rubric.md](./references/competency-rubric.md)
- Korean/English prose craft & AI-slop lexicon: [ko-en-prose-craft.md](./references/ko-en-prose-craft.md)
- Technical docs (RFC, ADR, Diátaxis, tech blog): [genre-technical.md](./references/genre-technical.md)
- Executive & strategic docs (6-Pager, SCQA, memo): [genre-executive.md](./references/genre-executive.md)
- Essays, columns & thought leadership: [genre-essay.md](./references/genre-essay.md)
- Persuasive, product copy & proposals: [genre-persuasive.md](./references/genre-persuasive.md)
- Golden Before/After exemplars: [before-after-ko-executive.md](./examples/before-after-ko-executive.md), [before-after-tech-essay.md](./examples/before-after-tech-essay.md)

## Verification Checklist
- [ ] Mode, single genre profile, and rigor tier were explicitly selected.
- [ ] Zero fabricated statistics, citations, or quotes (`[확인 필요]` used where data is missing).
- [ ] `prose_audit.py` ran on the final text (`ok: true`, zero `P0` blockers) and `--compare` ran on v1→v2 revisions.
- [ ] Adversarial review (`editorial-critic` for Flagship/Mode C, or 4-Protocol self-audit for Standard) confirmed Publish Gate (`>= 18/24`, starred dims `>= 2`, `0 P0`).
