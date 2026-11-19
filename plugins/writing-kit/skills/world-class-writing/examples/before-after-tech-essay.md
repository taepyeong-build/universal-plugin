# Golden Example: Korean Tech Essay & Editorial Critic Review

Genre: `essay` | Mode: `C (Critique)` → `B (Rewrite)` | Rigor Tier: `Flagship`

---

## 1. Before — AI-Slop Essay Draft (v1)

```markdown
# 서론

오늘날 급변하는 AI 시대에 개발자의 역할은 빠르게 변하고 있습니다. 많은 사람들은 코드 작성이 자동화되는 것에 대해 걱정합니다. 하지만 핵심은 바로 AI는 단순히 코드를 짜는 도구가 아니라 사고의 파트너라는 점입니다.

## 본론

- **생산성 향상:** 반복적인 보일러플레이트 작성을 줄여줍니다.
- **학습 가속:** 새로운 프레임워크를 빠르게 탐색하게 도와줍니다.
- **품질 개선:** 테스트 코드 생성을 통해 안정성을 높입니다.
- **협업 강화:** 문서화 부담을 덜어 팀 소통을 매끄럽게 합니다.

이러한 변화는 다양한 측면에서 긍정적인 효과로 보여진다. 개발자는 더 높은 추상화 수준에서 시스템을 설계하는 것이 가능하다.

## 결론

지금까지 AI 시대 개발자의 변화를 살펴보았습니다. 앞으로의 행보가 기대됩니다.
```

---

## 2. Independent `editorial-critic` Scorecard (v1)

- **Executive Verdict**: **FAIL (Publish Gate Rejected — 4/24, 3 P0 blockers)**
- **Deterministic Evidence (`prose_audit.py --genre essay`)**:
  - `ok: false` (8 errors, 5 warnings): `slopHits: 6`, `doublePassiveHits: 1` (`보여진다`), `boldBulletRatio: 57.1%` (> 20% P0 limit), `burstinessCV: 0.236` (< 0.30 floor), `concreteAnchors: 0`, `genericHeadingCount: 3`.
- **W1–W8 Summary**: W1 `1`, W2 `0` (P0: fails Negation Test), W3 `0`, W4 `1`, W5 `0`, W6 `1` (P0: double passive + flat CV), W7 `0` (P0: 6 slop hits + bold-bullet bloat), W8 `1`.
- **Steelman Counter-Argument Missing**: Ignores the real case that AI-generated tests share the same blind spots as AI-generated implementation code.
- **10–15% Deletion Candidates**: Cut lines 1 (`# 서론`), 3 (`오늘날 급변하는...`), 15–17 (`# 결론` + recap/optimism closing) — >30% removable boilerplate.

---

## 3. After — World-Class Essay Revision (v2)

```markdown
# 코드가 공짜가 되자 설계의 빚이 10배 빨라졌다

지난달 한 엔지니어가 AI 에이전트로 2시간 만에 1,400줄짜리 결제 연동 모듈을 올렸다. 24개 테스트는 전부 초록불, 코드 리뷰도 10분 만에 끝났다. 그런데 금요일 밤 11시 장애 경보가 울린다. 타임아웃 재시도가 멱등성 키를 빼먹어 같은 고객 카드를 세 번 긁은 것이다.

## 병목은 구현 속도에서 경계 조건 검증으로 이동했다

코드 생성 비용이 0에 수렴할수록 팀이 치르는 진짜 비용은 "무엇을 만들지 말아야 하는가"를 결정하는 시간으로 몰린다. 예전에는 1,400줄을 손으로 치는 사흘 동안 개발자가 자연스럽게 예외 흐름을 의심했다. 손이 느렸기에 머리가 따라붙었다. 이제는 초안이 5분 만에 완성되니, 검토하지 않은 가정이 그대로 프로덕션에 쌓인다.

물론 AI가 정적 분석과 테스트 생성을 자동화해 실수를 줄여 준다는 반론도 설득력이 있다. 맞는 말이다. 다만 자동 생성된 테스트는 구현을 쓴 바로 그 모델의 맹점을 그대로 복제하기 쉽다. 멱등성 키 누락을 구현에서 놓친 모델은 테스트에서도 그 시나리오를 빠뜨린다.

## 살아남는 개발자의 무기: 결정론적 가드레일 설계

그래서 시니어 엔지니어의 핵심 역량은 코딩 속도가 아니라 실패 경계를 코드로 못 박는 힘으로 바뀐다. 프롬프트로 "중복 결제하지 마"라고 부탁하는 대신, 데이터베이스 유니크 제약과 멱등성 테스트를 하네스에 고정한다.

생성 비용이 사라진 시대에 비싸지는 것은 언제나 검증이다. 내일 아침 리뷰할 PR에서 줄 수부터 보지 말자. 어떤 실패가 아직 테스트에 없는지부터 묻자.
```

---

## 4. Verified `--compare` Proof (`v1 → v2`)

| Metric | Before (v1) | After (v2) | Delta |
| :--- | :---: | :---: | :---: |
| `prose_audit.py --genre essay --strict` | **FAIL** (8 err / 5 warn) | **PASS** (0 err / 0 warn) | **-8 err / -5 warn** |
| Bold-Lead Bullet Ratio | 57.1% (P0) | 0.0% | -57.1% |
| Burstiness CV (Rhythm) | 0.236 (flat) | 0.391 (varied) | **+0.155** |
| AI Slop / Double Passive | 6 / 1 | 0 / 0 | -6 / -1 |
| Concrete Anchors | 0 | 8 | +8 |
| Publish Gate (W1–W8) | 4/24 (FAIL) | 22/24 (PASS, ★ W2/W6/W7 = 3/3/3) | +18 |
