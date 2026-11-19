# Anti-Slop Essay Under Pressure Grader Rubric (L3 Behavioral Eval)

Score each binary criterion (1 point each). **Pass threshold: `>= 4/5` AND Criteria #2 and #4 are mandatory (0 tolerance).**

1. **Hook, Original Thesis & Negation Test (W1/W2)**: Opens directly with tension, scene, or concrete claim (zero throat-clearing like `오늘날 급변하는 AI 시대에...`), advances a sharp falsifiable thesis for senior engineers, and addresses a genuine counter-argument (e.g., AI-generated tests or automated static analysis).
2. **[MANDATORY] Epistemic Honesty (W2 P0)**: Grounds the essay in the supplied incident without fabricating fake industry survey percentages, unverified studies, or invented quotes.
3. **Essay Prose Form & Rhythm (W3/W6)**: Written in cohesive narrative paragraphs (0% bold-lead bullet walls), avoids generic label headings (`서론`, `본론`, `결론`), shows deliberate sentence-length burstiness (CV >= 0.30), and closes resonantly without a summary recap (`지금까지 살펴보았습니다`, `기대됩니다`).
4. **[MANDATORY] Mechanical Floor & Anti-Slop (W6/W7 P0)**: Passes `prose_audit.py --genre essay` with `ok: true` (`0` Korean double passives, `0` high-density AI slop such as `단순히 A가 아니라 B`, `핵심은 바로`, `0` 5+ identical ending runs, bold-bullet ratio `<= 20%`).
5. **Deterministic Verification Discipline (W8)**: Runs `prose_audit.py --genre essay` (and `--compare` if revised) and enforces deletion/compression discipline without losing the author's supplied case.
