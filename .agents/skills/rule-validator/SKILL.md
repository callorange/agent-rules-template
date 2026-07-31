---
name: rule-validator
description: rules/ 디렉터리 내의 규칙 모듈 및 dist/ 배포 번들의 무결성(금지 표현, UTF-8 인코딩, 깨진 상대 링크, 필수 코어 모듈 누락)을 정적으로 검증하고, 대규모 개정 시 규칙 간 상호 충돌 및 의미적 모호성을 진단할 때 사용합니다.
---

# Rule Validator Skill (규칙 무결성 정적 검증 및 의미 진단 스킬)

본 스킬은 `agent-rules-template` 레포지토리의 `rules/` 모듈 및 `dist/AGENTS.md` 파일들이 프로젝트 헌법 및 무결성 규격을 준수하는지 정적으로 검증하고, 모듈 간 의미적 정합성을 진단할 때 활성화하여 사용합니다.

---

## ⚙️ 1. 실행 환경 및 런타임 Fallback (Prerequisites)

규칙 검증 스크립트는 실행 환경에 따라 아래 우선순위에 맞춰 런타임 명령어를 선택하여 구동합니다:

1. **`uv` 환경**: `uv run python .agents/skills/rule-validator/scripts/validate_rules.py`
2. **Linux / macOS**: `python3 .agents/skills/rule-validator/scripts/validate_rules.py`
3. **Windows / 일반 Python**: `python .agents/skills/rule-validator/scripts/validate_rules.py` 또는 `py .agents/skills/rule-validator/scripts/validate_rules.py`

> ⚠️ **Python 런타임 미설치 환경 시**:
> 만약 런타임(Python 3 / uv)이 전혀 구성되어 있지 않은 환경인 경우, 에이전트는 프롬프트 상에서 무리하게 정규식을 계산하지 말고 사용자에게 `"Python 3 런타임이 필요합니다. 정적 검사를 스킵합니다."`라는 경고를 보고하고 정적 검사를 스킵합니다.

---

## 🔒 2. Phase 1: 기계적 정적 검사 (Deterministic Static Check - 필수/차단형)

규칙 모듈을 수정하거나 새로 작성한 후, 반드시 런타임 스크립트를 구동하여 검증을 통과해야 합니다.

### 🎯 검사 항목
* **필수 코어 모듈 존재 여부**: `rules/core/` 내 base 최상위 헌법 모듈 존재 확인 및 `rules/core/*.md` 동적 탐색
* **UTF-8 인코딩**: 한글 깨짐 방지를 위한 올바른 UTF-8 디코딩 검사
* **YAML Frontmatter 검사**: 스킬(`SKILL.md`) 및 서브에이전트(`subagents/*.md`)의 필수 메타데이터(`name`, `description`) 존재 여부 검사
* **금지된 출력 생략 표현**: `... (중략) ...`, `// 기존 내용과 동일`, `[나머지 부분 생략]` 등 무단 생략 구문 삽입 여부 검사 (단, 인라인 백틱 및 코드 블록 내부 안내 예시는 제외)
* **상대 경로 링크 유효성**: 원본 및 `dist/` 배포 아티팩트 내 Markdown 문서의 상대 파일 링크 실재 존재 여부 확인
* **Stale Dist 동기화 상태 검사**: 원본 소스 파일 대비 `dist/` 배포 아티팩트의 최신화 여부 검사 및 경고 출력

### 🛠️ 실패 시 복구 프로토콜
1. 스크립트 실행 실패 시 출력된 에러 위치(`[파일명:줄번호]`)를 확인합니다.
2. 수술적 편집(Surgical Edit) 도구를 사용하여 해당 위치의 깨진 링크나 금지 표현을 수정합니다.
3. 수정 후 스크립트를 재실행하여 `✅ 모든 원본 규칙 모듈, dist/ 배포 아티팩트 및 Markdown 파일 검증을 성공적으로 통과하였습니다!` 메시지를 확인합니다.

---

## 💡 3. Phase 2: 의미적 정합성 권고 진단 (Semantic Advisory Audit - 선택/권고형)

규칙 모듈을 신규 작성·대규모 개정하거나, 에이전트가 판단하기에 규칙 간 상호 충돌 및 모호성이 의심되는 경우, 또는 사용자의 지시가 있을 때 `auditor` 서브에이전트 지침 및 LLM 지능을 활용하여 아래 5대 관점에서 선택적 진단을 수행합니다.

### 📋 진단 체크리스트 (Advisory Rubric)

1. **상호 충돌 (Conflict) 진단**:
   * 최상위 헌법 모듈(`01-base.md`)의 원칙과 하위 `frameworks/`, `architecture/`, `styles/` 특화 규칙이 정면으로 충돌하는 부분이 있는가? (단, 의도된 하위 모듈의 Override 조항은 제외)
2. **의미적 모호성 (Ambiguity) 진단**:
   * 에이전트가 실행 시 주관적으로 오해하거나 자율적으로 다르게 해석할 수 있는 불명확한 표현("적절히 처리한다", "상황에 따라 다름" 등)이 존재하는가?
3. **실효성 및 중복 (Redundancy) 진단**:
   * 서로 다른 모듈 간 완전히 동일한 지시가 불필요하게 반복되거나, 사장되어 실효성을 잃은 구문이 있는가?
4. **아티팩트 격리 (Isolation) 진단**:
   * 프로젝트 헌법 VI조에 따라 이 프로젝트 전용 내부 메타(`/.agents/`) 요소가 외부 배포용 모듈(`/rules/`, `/skills/`, `/subagents/`)로 잘못 유출·오염되었는가?
5. **오버엔지니어링 & ROI (Over-engineering & Value) 진단**:
   * 단순 쉘 명령어 1줄이나 수작업으로 끝날 일에 불필요한 규칙, 스킬, 서브에이전트 래퍼를 씌워 토큰 및 레이턴시 오버헤드를 야기하는 구문이 있는가?

> 📢 **진단 보고 프로토콜**:
> Phase 2 진단 결과는 빌드를 차단하는 Error가 아닌 **'권고 보고서(Advisory Report)'** 형태로 사용자에게 제시하며, 사용자의 승인을 얻은 후에만 가이드를 반영합니다.
