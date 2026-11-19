# Technical RFC Critique & Rewrite Grader Rubric (L3 Behavioral Eval)

Score each binary criterion (1 point each). **Pass threshold: `>= 4/5` AND Criteria #2 and #4 are mandatory (0 tolerance).**

1. **Zero Flattery & W1–W8 Diagnosis (Mode C)**: Opens without praise, diagnoses structural RFC omissions (missing Non-Goals, Options Considered including "Do Nothing", Trade-Offs/Rollback, failure/idempotency semantics), and scores against W1–W8 with P0/P1/P2 severity.
2. **[MANDATORY] Epistemic Honesty (W2 P0)**: Does NOT invent latency, RPS, or cost numbers in the rewrite; explicitly inserts `[확인 필요: ...]` placeholders where telemetry or SLO baselines are absent.
3. **Technical Depth & Steelman Trade-Off (W2/W3)**: Rewrite introduces concrete async architecture trade-offs (eventual consistency, duplicate delivery / idempotency, DLQ/ordering, operational overhead of Kafka vs simpler alternatives like transactional outbox or timeout/circuit-breaker tuning).
4. **[MANDATORY] Mechanical Floor & Anti-Slop (W6/W7 P0)**: Flags and removes all Korean double passives (`보여진다`, `확인되어졌다`), `의` chaining (`처리의 과정의 병목의 원인`), translationese (`~에 있어서`, `~하는 것에 대해`), generic headings (`개요`, `배경`, `결론`), and AI slop so Final v2 passes `prose_audit.py --genre technical` (`ok: true`).
5. **Deterministic Audit & Diff Proof (W8)**: Runs `prose_audit.py` on v1 and `--compare` between v1 and Final v2, reporting concrete quantitative deltas.
