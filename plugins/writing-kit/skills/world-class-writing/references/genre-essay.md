# Genre Profile: Essay, Journalism & Thought Leadership (`essay`)

**Target Documents**: Long-Form Essays, Newsletters, Op-Eds, Analytical Columns, Founder Letters, Cultural/Tech Commentary (*The Economist*, *The New Yorker*, Paul Graham, Zinsser standard).
**Starred Dimensions (must be `>= 2` each)**: **W2 (Original Thesis & Insight) ★, W6 (Micro-Prose & Rhythm) ★, W7 (Voice Authenticity & Anti-Slop) ★**.

---

## 1. Structural Architecture

Unlike executive memos, great essays earn attention through **intellectual tension and discovery**, not corporate templates:

1. **Opening Hook (Tension, Scene, or Counter-Intuitive Claim)**:
   - Enter *in medias res* with a sharp observation, concrete anecdote, or paradoxical fact.
   - Zero warm-up paragraphs (`오늘날 AI 시대에...`). Cut your first drafted paragraph if sentence #4 is where the essay actually begins.
2. **Deepening the Question (Exploration & Evidence)**:
   - Unpack why the conventional wisdom feels reasonable — steelman the status quo before overturning it.
   - Move continuously down Hayakawa's Ladder of Abstraction: ground every abstract idea in a concrete story, mechanism, historical parallel, or lived detail.
3. **The Turn (Insight / Reframing)**:
   - Deliver the non-obvious conceptual hinge that changes how the reader sees the subject.
   - A great essay leaves the reader with a **new mental model or sharper vocabulary**, not a 5-point checklist.
4. **Resonant Close (No Summary Recap)**:
   - Never write `"지금까지 ~을 살펴보았습니다. 앞으로 ~가 중요합니다."`
   - Close with a widened implication, a crisp echo of the opening image, or a single stark sentence that lingers.

---

## 2. Genre-Specific Editorial Rules

1. **Prose Over Slide-Deck Formatting**:
   - Write in cohesive paragraphs. Ban mechanical `- **키워드:** 설명` bold-lead bullet walls (`prose_audit.py` enforces this as a **P0 error** above 20% in `essay` mode).
   - Avoid excessive subheadings every 2 paragraphs; let paragraph transitions carry momentum.
2. **Rhythmic Burstiness (Prosody)**:
   - Alternate expansive, layered sentences (building tension or nuance) with stark, short sentences (landing the point). Target sentence-length CV `>= 0.35–0.40`.
   - Read aloud mentally: cut clumsy consonant clusters, repeated Korean endings (`~다. ~다. ~다.`), and stacked `의` chains.
3. **Earned Voice & Precision Over Ornament**:
   - Clarity *is* style (*Zinsser / Orwell*). Prefer a vivid concrete noun and an active verb over three adjectives.
   - Maintain consistent emotional temperature — authoritative, curious, wry, or candid — without sliding into preachiness or melodrama.
4. **Surprise Per Paragraph**:
   - Every paragraph must introduce a fresh turn, concrete illustration, or counter-perspective. If a paragraph merely restates the previous paragraph in different words, cut it.

---

## 3. Audit Calibration (`--genre essay`)

- **Strict checks**: Bold-lead bullet ratio `<= 20%` (P0 error above), high burstiness (CV `>= 0.30` warning floor, `>= 0.40` target), zero AI-slop clichés (`단순히 A가 아니라 B`, `핵심은 바로`, `delve`, `tapestry`), zero Korean double passives, varied sentence endings.
- **Thesis Gate**: Strict **Negation Test** — if no thoughtful reader could disagree with your thesis, rewrite the thesis before drafting.
