# Golden Example: Korean Executive Decision Memo (Before → Audit → After)

Genre: `executive` | Mode: `B (Rewrite)` | Rigor Tier: `Flagship`

---

## 1. Before — Default-LLM Draft (v1)

```markdown
# 배경

오늘날 급변하는 개발 환경에 있어서 코드 품질 관리는 그 어느 때보다 중요합니다. 최근 배포 과정에 있어서 장애가 팀에 의해 여러 차례 확인되어졌으며, 이는 단순히 기술의 문제가 아니라 협업 프로세스의 문제라고 할 수 있습니다.

## 제안 내용

핵심은 바로 혁신적인 솔루션을 도입하는 것입니다. 자동화 검증 도구의 도입의 추진의 방향을 검토를 진행하고 테스트를 실시하는 것이 가능합니다. 다양한 측면에서 시너지를 극대화할 수 있을 것으로 보여진다.

## 결론

지금까지 자동화 도입의 필요성을 살펴보았습니다. 앞으로의 조직의 성과가 기대됩니다.
```

---

## 2. Deterministic Audit + Editorial Diagnosis (v1)

- **`prose_audit.py --genre executive` Verdict**: **`FAIL` (`ok: false`, 12 errors, 6 warnings)**
  - `doublePassiveHits`: **2** (`확인되어졌으며`, `보여진다` — P0)
  - `slopHits`: **10** (`오늘날 급변하는`, `그 어느 때보다 중요`, `단순히 ... 아니라`, `라고 할 수 있습니다`, `핵심은 바로`, `혁신적인 솔루션`, `다양한 측면에서`, `시너지를 극대화`, `지금까지 ... 살펴보았습니다`, `기대됩니다` — P0)
  - `translationeseHits`: **3** (`~에 있어서` x2, `~에 의해`)
  - `uiChainCount`: **1** (`도구의 도입의 추진의 방향`)
  - `genericHeadingCount`: **2** (`배경`, `결론`)
  - `concreteAnchors`: **0**
- **Adversarial Critic Highlights**:
  - **W1 (0/3)**: No decision ask, owner, deadline, or scope.
  - **W2 (0/3)**: Fails Negation Test ("코드 품질 관리는 중요하다"), zero numbers, zero counter-argument.
  - **W3 (0/3)**: Vague label headings (`배경`, `결론`), buried recommendation.

---

## 3. After — World-Class Revision (v2)

```markdown
# 4분기 배포 장애를 절반으로 줄이려면 모델 교체보다 CI 사전 검증에 2주를 먼저 투자해야 한다

**의사결정 요청**: 2026년 11월 25일까지 플랫폼팀 엔지니어 1명을 배정해 PR 병합 전 정적 스키마·계약 검증 게이트를 도입하는 안건을 승인해 달라.

## 장애 27건 중 19건이 병합 직전 설정 오류에서 터졌다

지난 3분기 프로덕션 롤백 27건을 원인별로 분류하니 19건(70%)이 아키텍처 결함이 아닌 설정 오타와 스키마 불일치였다. 사람 리뷰어가 반복 규칙을 육안으로 걸러내느라 PR 1건당 평균 18시간이 묶였다. 결정론적 사전 검증을 CI 앞단에 두면 리뷰어는 실패 모드와 경계 조건 판단에만 집중할 수 있다.

## 초기 규칙 튜닝 비용 3일이 들지만 2주 경고 모드로 오탐 리스크를 통제한다

가장 강한 반론은 "검증 게이트가 긴급 배포 속도를 늦춘다"는 우려다. 타당한 지적이다. 그래서 첫 2주는 차단 없는 경고 모드로 운영해 오탐률을 5% 미만으로 낮춘 뒤 차단 모드로 전환한다. 대안으로 검토한 전수 수동 체크리스트는 팀 규모가 12명을 넘기며 이미 준수율이 떨어졌다.

## 실행 일정과 성공 기준

- **1주차 (11/25~12/01, DRI: 플랫폼 리드)**: 핵심 3종 스키마 검증 스크립트 CI 연동 및 경고 모드 가동.
- **2주차 (12/02~12/08)**: 오탐 사례 정리 및 5% 미만 달성 확인.
- **종료 기준 (60일 후 점검)**: 설정 오류 기인 롤백 월 [확인 필요: 목표 건수] 이하, PR 평균 대기 시간 6시간 미만 달성. 미달 시 게이트를 축소한다.
```

---

## 4. Verified `--compare` Proof (`v1 → v2`)

| Metric | Before (v1) | After (v2) | Delta |
| :--- | :---: | :---: | :---: |
| `prose_audit.py --strict` | **FAIL** (12 err / 6 warn) | **PASS** (0 err / 0 warn) | **-12 err / -6 warn** |
| Korean Double Passives | 2 | 0 | -2 |
| AI Slop Hits | 10 | 0 | -10 |
| Korean Translationese | 3 | 0 | -3 |
| Generic Label Headings | 2 | 0 | -2 |
| Concrete Anchors | 0 | 18 | +18 |
| Epistemic Honesty | Unverified fluff | Explicit `[확인 필요: 목표 건수]` | P0 Gate Pass |
