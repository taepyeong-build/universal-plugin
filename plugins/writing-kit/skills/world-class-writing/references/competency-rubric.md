# 8-Dimension World-Class Writing Competency Rubric (W1–W8)

Ground every editorial critique and revision in this two-tier evaluation model: **Three P0 Hard Gates** (non-negotiable floor) plus **Genre-Weighted Excellence Targets** across eight MECE writing dimensions (`0–3` each, `/24` total).

---

## 1. Tier 1 — Three P0 Hard Gates (Zero Tolerance)

A draft **FAILS** automatically if **any** of the following P0 defects remain, regardless of total score:

1. **Epistemic Honesty Gate (W2)**: Any invented statistic, benchmark, percentage, quote, or citation. Unverified quantitative claims must be marked `[확인 필요: 구체 지표/근거]`.
2. **Thesis Value Gate (W1/W2)**:
   - *Analytical / Persuasive / Executive / Essay*: Must pass the **Negation Test** — could an intelligent, well-informed skeptic plausibly argue the opposite of the central thesis? ("AI 혁신이 중요하다" fails; "사내 AI 도입은 모델 교체보다 평가 하네스 구축에 예산의 60%를 배정해야 성공한다" passes.)
   - *Pure Reference / Tutorial / Runbook*: Must pass the **Reader Actionability Test** — can the target reader execute the exact task or decision without external guesswork?
3. **Mechanical Language Floor Gate (W6/W7)**: `prose_audit.py` must return `ok: true` (`exit 0`) — zero Korean double passives (`보여지다`, `쓰여지다`, `되어지다`), zero high-density AI slop, zero 5+ consecutive identical endings, and zero essay bold-lead bullet bloat.

---

## 2. Tier 2 — W1–W8 Scoring Matrix (`0–3` Scale)

### W1. Audience Modeling & Rhetorical Intent (*Kellogg Knowledge-Crafting / Pinker / Kairos*)
- **0 (L1 Failing)**: Unclear who reads or why; suffers severely from Curse of Knowledge or talks down with obvious background.
- **1 (L2 Competent)**: General audience implied, but entry hook is slow and desired reader shift/decision is vague.
- **2 (L3 Senior)**: Target reader, assumed baseline, and value proposition are clear within the first two paragraphs; register fits context.
- **3 (L4 World-Class)**: Precisely anticipates reader beliefs, objections, and incentives; every section advances a concrete decision or mental-model shift.

### W2. Epistemic Rigor & Argument Architecture (*Toulmin / Steelmanning / Amazon 6-Pager*)
- **0 (L1 Failing)**: Fails Negation Test, contains fabricated data, or ignores obvious counter-arguments and trade-offs.
- **1 (L2 Competent)**: Reasonable claim, but warrants are implicit, evidence is mostly anecdotal, or counter-arguments are strawmanned.
- **2 (L3 Senior)**: Clear Claim → Evidence → Warrant chain; explicitly states scope limits, uncertainty, and real trade-offs.
- **3 (L4 World-Class)**: Non-obvious, falsifiable thesis; steelmans the sharpest objection and resolves or prices its cost transparently.

### W3. Macro-Structure & Information Architecture (*Minto Pyramid / SCQA / Diátaxis / Narrative Arc*)
- **0 (L1 Failing)**: Generic topic-label headings (`서론`, `본론`, `결론`, `개요`); buried conclusion; orphan or multi-topic paragraphs.
- **1 (L2 Competent)**: Logical sequence exists, but headings merely name topics instead of carrying assertions or reader actions.
- **2 (L3 Senior)**: Matches genre macro-architecture; reverse outline alone conveys the complete argument; clean paragraph unity.
- **3 (L4 World-Class)**: Effortless scannability and intellectual momentum; structural geometry directly reinforces the thesis.

### W4. Local Cohesion & Logical Flow (*Joseph Williams Given-New Contract*)
- **0 (L1 Failing)**: Abrupt subject jumps between sentences; propped up by empty connectors (`또한`, `한편`, `더 나아가`, `Additionally`).
- **1 (L2 Competent)**: Readable locally, but several transitions rely on mechanical glue rather than conceptual continuity.
- **2 (L3 Senior)**: Sentences consistently anchor known context early (Topic) and place new emphasis at the end (Stress); transitions signal real logic (cause, contrast, concession).
- **3 (L4 World-Class)**: Invisible propulsion — deleting explicit conjunctions still leaves the logical sequence unmistakable.

### W5. Signal Density & Ladder of Abstraction (*Hayakawa / Tufte / Zinsser*)
- **0 (L1 Failing)**: Throat-clearing intro, repetitive padding, abstraction plateau without concrete mechanisms/numbers/cases, hollow wrap-up.
- **1 (L2 Competent)**: Some concrete details, but >= 20% of words can be cut without losing meaning.
- **2 (L3 Senior)**: High signal-to-noise ratio; principles are anchored within 1–2 sentences by verifiable mechanisms, examples, or numbers.
- **3 (L4 World-Class)**: Every sentence pays rent; zero redundant clauses; effortless vertical movement between principle and concrete detail.

### W6. Micro-Prose Craft, Rhythm & KO/EN Linguistic Mastery (*Williams / Orwell / 이오덕*)
- **0 (L1 Failing)**: Korean double passives, heavy translationese (`~에 있어서`, `~에 의해`, `의` chaining), monotonous sentence lengths or 5+ identical endings.
- **1 (L2 Competent)**: Grammatically acceptable, but relies heavily on nominalizations (`진행을 실시하다`, `make a decision`) and uniform sentence cadence.
- **2 (L3 Senior)**: Actor = Subject, Action = Verb; clean Korean particles and varied endings; deliberate short/long rhythm contrast.
- **3 (L4 World-Class)**: Crisp, energetic prose with intentional burstiness; sentences land their key insight precisely on the final stress beat.

### W7. Voice Authenticity & Anti-Slop Discipline
- **0 (L1 Failing)**: Unmistakable LLM fingerprints (`단순히 A가 아니라 B`, `오늘날 급변하는`, `delve`, `tapestry`, compulsive 3-item lists, bold-bullet spam).
- **1 (L2 Competent)**: Mostly clean of clichés, but sounds generic, corporate, or emotionally flat for its genre.
- **2 (L3 Senior)**: Zero AI slop; distinct, consistent editorial temperature calibrated to genre and audience.
- **3 (L4 World-Class)**: Unmistakably human authority and clarity; voice sharpens rather than distracts from the argument.

### W8. Verification, Deterministic Audit & Multi-Pass Revision
- **0 (L1 Failing)**: Single-pass output claimed "polished" without running `prose_audit.py` or checking factual/structural gaps.
- **1 (L2 Competent)**: Audit run once, but warnings ignored or edits limited to surface synonyms without structural compression.
- **2 (L3 Senior)**: `prose_audit.py` clean (`ok: true`), adversarial protocol executed, measurable v1→v2 reduction in defects or bloat.
- **3 (L4 World-Class)**: Full `--compare` delta proof showing cleaner metrics, tighter compression, and intact or strengthened evidence.

---

## 3. Genre Weight Matrix & Publish Gate

**Publish Gate**: Total **`>= 18 / 24`**, **`0 P0` defects**, and every **starred dimension (`★`) `>= 2`**.

| Genre Profile | Starred Dimensions (`★`, must be >= 2) | Primary Structural Standard | Coaching-Flexible Dimensions |
| :--- | :--- | :--- | :--- |
| **`technical`** | **W2 ★, W3 ★, W5 ★** | RFC/ADR or Diátaxis 4-Quadrant | W7 (restrained clarity over literary flair) |
| **`executive`** | **W1 ★, W2 ★, W3 ★** | BLUF + SCQA + MECE + Decision Ask | W6/W7 (high-clarity prose over stylistic experimentation) |
| **`essay`** | **W2 ★, W6 ★, W7 ★** | Hook → Exploration → Turn → Insight | W3 (narrative discovery allowed over BLUF) |
| **`persuasive`** | **W1 ★, W5 ★, W7 ★** | JTBD / Pain → Mechanism → Proof → Single CTA | W3 (conversion arc over neutral balance; still honest on scope) |
| **`general`** | **W1 ★, W2 ★, W5 ★** | Core W1–W8 + user sample mirror | Calibrate to explicit user target |

---

## 4. Finding Severity Definitions

- **`P0` (Blocker)**: Hard Gate violation (fabricated fact, Negation Test failure, `prose_audit.py` error, broken core logic). Must be fixed before delivery.
- **`P1` (Major)**: Weakens reader trust or clarity (starred dimension `< 2`, missing counter-argument, buried conclusion, heavy translationese/nominalization, >15% removable bloat). Fix in revision pass.
- **`P2` (Polish)**: Optional cadence, metaphor, or micro-wording upgrade once P0 and P1 are resolved.
