# Universal Expert Plugins (한국어 요약 안내)

> 영문 공식 문서([README.md](./README.md))의 핵심 요약입니다. 최신 변경과 세부 명세는 영문 문서를 기준으로 삼습니다.

단일 스펙에서 **Claude Code**, **Codex CLI**, **Antigravity CLI**(`claude`, `codex`, `agy`)용 플러그인을 빌드하고 검증합니다. 모든 런타임은 외부 패키지 없이 Python 3.9+ 표준 라이브러리만 씁니다.

## 제공 플러그인

| 플러그인 | 버전 | 카테고리 | 구성 요소 | 핵심 기능 |
| :--- | :---: | :--- | :--- | :--- |
| [`expert-kit`](./plugins/expert-kit/README.md) | `1.0.0` | Developer Tools | Skills, Rules, Hooks, MCP, Subagent, Scripts, Evals (1) | 7차원 아키텍처 리뷰(`architecture-review`), 셸 안전·종료 검증 훅, 컨텍스트 예산 점검용 stdio MCP 서버, 읽기 전용 `arch-reviewer` 서브에이전트 |
| [`writing-kit`](./plugins/writing-kit/README.md) | `1.0.0` | Productivity | Skills, Rules, Subagent, Scripts, Evals (3) | W1–W8 글쓰기 워크플로(`world-class-writing`), 온디맨드 장르 프로파일 4종, 한·영 문체 감사 도구(`prose_audit.py`), 읽기 전용 `editorial-critic` 서브에이전트 |

세부 훅 정책, 환경 변수, 단독 검증 명령은 각 플러그인의 영문 문서([expert-kit](./plugins/expert-kit/README.md), [writing-kit](./plugins/writing-kit/README.md))를 참고하세요.

## CLI별 설치 방법

### Claude Code
```text
/plugin install expert-kit --marketplace taepyeong-build/universal-plugin
/plugin install writing-kit --marketplace taepyeong-build/universal-plugin
```

### Codex CLI
```bash
codex plugin marketplace add https://github.com/taepyeong-build/universal-plugin
codex plugin add expert-kit@universal-plugins
codex plugin add writing-kit@universal-plugins
```

Codex CLI는 스킬, 규칙, 서브에이전트를 설치 즉시 활성화합니다. 워크스페이스 훅(`com.openai/hooks.json`)은 자동 적용되지 않아 필요한 저장소에서 직접 채택해야 합니다.

### Antigravity CLI
```bash
agy plugin install https://github.com/taepyeong-build/universal-plugin/tree/main/plugins/expert-kit
agy plugin install https://github.com/taepyeong-build/universal-plugin/tree/main/plugins/writing-kit
```

## 로컬 개발과 3계층 검증

로컬 실행에는 **Python 3.9+**가 필요합니다. `python3 tools/verify.py`는 `PATH`에 `claude`, `codex`, `agy`가 모두 있어야 통과하며, 하나라도 빠지면 L1 검증에서 멈춥니다. `--with-evals` 옵션은 `claude` CLI로 L3 행동 평가를 돌리므로 LLM 토큰 비용이 듭니다.

```bash
# 1. 단일 스펙에서 3-CLI 어댑터와 마켓플레이스 카탈로그 3종 재생성
python3 tools/sync.py

# 2. L1(스펙 드리프트·3-CLI 엄격 검증)과 L2(단위 테스트·doctor --ci) 실행
python3 tools/verify.py

# 3. 새 플러그인 스캐폴딩 생성(기본 스킬·규칙 + 선택형 hooks, MCP, agents, evals)
python3 tools/new_plugin.py my-plugin --description "Custom workflow plugin." --with-hooks --with-mcp

# 4. 선택형 L3 행동 평가 실행(claude CLI 필요)
python3 tools/verify.py --with-evals
```

생성된 어댑터(`plugin.json`, `.claude-plugin/*`, `hooks.json`, `mcp*.json`, `.mcp.json`, `com.openai/*`, `agents/*.md`, 루트 마켓플레이스 파일)는 직접 고치지 마세요. `registry.json`이나 `plugins/*/spec/*.json`을 수정한 뒤 `python3 tools/sync.py`와 `python3 tools/verify.py`를 차례로 실행하면 됩니다.

## 핵심 설계와 트레이드오프

| 영역 | 설계 방식 | 트레이드오프 / 경계 |
| :--- | :--- | :--- |
| **단일 스펙(SSOT) 컴파일** | `tools/sync.py`가 `registry.json`과 `plugins/*/spec/*.json`에서 마켓플레이스 3종과 `hooks`·`mcp`·`agents` 어댑터를 생성함. `skills/`·`rules/`는 빌드 없이 직접 배포함. | 스펙 수정 후 `tools/sync.py` 재실행이 필수이며, 누락 시 `tools/sync.py --check`가 드리프트를 차단함. |
| **무충돌 경로 분리** | `plugins/<name>/` 안에서 CLI별 어댑터 경로(`hooks.json`: Antigravity, `.claude-plugin/hooks.json`: Claude Code, `com.openai/hooks.json`: Codex)를 격리함. | Codex 훅은 설치만으로 켜지지 않아 `com.openai/hooks.json`을 워크스페이스에 직접 채택해야 함. |
| **표준 라이브러리 전용 런타임** | 훅, `doctor.py`, MCP 서버, `prose_audit.py`가 `pip`·`npm` 없이 Python 3.9+ 표준 라이브러리로만 동작함. | `schemas/`는 런타임 전체 검증 대신 IDE `$schema` 작성 가이드 역할을 맡음. |
| **3계층 검증 게이트** | `tools/verify.py` 기본 실행이 L1(SSOT 드리프트·3-CLI 검증·설치 테스트)과 L2(`unittest`·`doctor.py --ci`)를 매번 점검함. | 일상 검증을 결정적이고 무비용으로 유지하려고 L3 평가(`evals/`)는 `--with-evals` 선택 실행으로 분리함. |
