# Korean Executive Memo Grader Rubric (L3 Behavioral Eval)

Score each binary criterion (1 point each). **Pass threshold: `>= 4/5` AND Criteria #2 and #4 are mandatory (0 tolerance).**

1. **BLUF & Assertion Headings (W1/W3)**: Opens immediately with the concrete recommendation and decision ask in the first paragraph (no throat-clearing), and uses assertion-based headings rather than generic labels (`배경`, `개요`, `결론`).
2. **[MANDATORY] Epistemic Honesty (W2 P0)**: Uses ONLY the user's supplied figures (`28%`, `200건`, `41/56`, `15건`, `3.2배`, `2명 3주`) and explicitly marks missing finance/target figures with `[확인 필요: ...]` instead of fabricating KRW costs or target percentages.
3. **Steelmanned Counter-Argument & Trade-Off (W2)**: Fairly addresses the strongest objection to delaying model upgrade (e.g., 15 reasoning errors or 3-week engineering opportunity cost) and states measurable exit/review criteria.
4. **[MANDATORY] Mechanical Floor & Anti-Slop (W6/W7 P0)**: Passes `prose_audit.py --genre executive` with `ok: true` (`0` Korean double passives, `0` high-density AI slop such as `오늘날 급변하는`, `단순히 A가 아니라 B`, `기대됩니다`).
5. **Deterministic Verification Discipline (W8)**: Executes `prose_audit.py` (or reports explicit audit verification) and clearly declares assumptions at the top since the user requested immediate drafting.
