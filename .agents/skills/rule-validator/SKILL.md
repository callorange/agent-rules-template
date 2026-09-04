---
name: rule-validator
description: rules/, guides/, skills/, subagents/ 원본과 dist/ 배포 아티팩트의 기계적 무결성을 검사하고, 요청 또는 위험 조건에 따라 의미적 정합성을 권고 진단할 때 사용합니다.
---

# Rule Validator Skill (규칙 무결성 정적 검증 및 의미 진단 스킬)

본 스킬은 `agent-rules-template` 레포지토리의 `rules/`, `guides/`, `skills/`, `subagents/` 원본과 `dist/` 배포 아티팩트의 기계적 무결성을 검사합니다. 필요할 때는 별도의 의미적 권고 진단으로 문서와 규칙의 정합성을 검토합니다.

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

검사 대상 원본 또는 배포 아티팩트를 수정한 후에는 런타임 스크립트를 구동하여 검증합니다. `guides/`도 UTF-8, 상대 링크, 배포 최신성 같은 기계적 검사의 대상이지만 비규범적 참고 문서라는 성격은 유지합니다.

### 🎯 검사 항목
* **필수 Core 모듈 존재 여부**: `rules/core/` 내 최상위 헌법 모듈 존재 확인 및 `rules/core/*.md` 동적 탐색
* **UTF-8 인코딩**: 한글 깨짐 방지를 위한 올바른 UTF-8 디코딩 검사
* **YAML Frontmatter 검사**: 스킬(`SKILL.md`) 및 공개 서브에이전트(`subagents/*.md`)의 필수 메타데이터(`name`, `description`) 존재 여부 검사
* **금지된 출력 생략 표현**: `... (중략) ...`, `// 기존 내용과 동일`, `[나머지 부분 생략]` 등 무단 생략 구문 삽입 여부 검사 (단, 인라인 백틱 및 코드 블록 내부 안내 예시는 제외)
* **상대 경로 링크 유효성**: `rules/`, `guides/`, `skills/`, `subagents/` 원본, 루트 `AGENTS.md`, `dist/` 내 Markdown 문서의 상대 파일 링크 실재 여부 확인
* **Stale Dist 동기화 상태 검사**: 임시 디렉터리에 생성한 번들과 committed `dist/` 배포 아티팩트의 파일 집합 및 바이트 내용을 결정적으로 비교하여 최신화 여부를 경고로 출력합니다. 이는 검증 실패가 아니라, 수정 후 `python scripts/build_dist.py`를 실행해야 하는 필수 후속 작업입니다.

### 🛠️ 실패 시 복구 프로토콜
1. 스크립트 실행 실패 시 출력된 에러 위치(`[파일명:줄번호]`)를 확인합니다.
2. 수술적 편집(Surgical Edit) 도구를 사용하여 해당 위치의 깨진 링크나 금지 표현을 수정합니다.
3. 수정 후 스크립트를 재실행하여 `✅ 모든 원본 규칙 모듈, dist/ 배포 아티팩트 및 Markdown 파일 검증을 성공적으로 통과하였습니다!` 메시지를 확인합니다.

---

## 💡 3. Phase 2: 의미적 정합성 권고 진단 (Semantic Advisory Audit - 선택/권고형)

Phase 2는 Phase 1의 결정적 정적 검사가 아닌, 문맥에 따른 의미적 권고 진단입니다. 자동 build failure를 만들지 않으며, 실제 conflict, ambiguity, over-prescription, scope 또는 authority 문제를 근거와 함께 보고합니다.

### Required Independent Review

다음 경우에는 독립 검토를 수행합니다.

* 사용자가 독립 감사 또는 검수를 명시적으로 요청한 경우
* 되돌릴 수 없는 운영 데이터 변환 또는 migration
* 실제 credential, authorization 또는 privilege boundary 변경

### Conditional Independent Review

일반 schema migration, architecture·deployment·rule 체계 변경, 가역적인 security-related configuration 변경은 다음 중 하나가 확인될 때만 독립 검토를 수행합니다.

* 결정적 test 또는 static validation으로 주된 위험을 검증할 수 없는 경우
* 대안 선택이 security, data integrity 또는 public contract에 영향을 주는 경우
* 독립 관점이 다른 방법으로 얻을 수 없는 evidence를 제공할 수 있는 경우

이 조건이 없는 변경에는 독립 검토를 자동 호출하지 않습니다.

### Guides의 Semantic Advisory 경계

`guides/`는 Phase 1의 기계적 검사 대상이지만 `rules/`와 같은 semantic strictness를 적용하지 않습니다. `권장한다`, `상황에 따라`, `예를 들어`, `고려할 수 있다` 같은 설명적 표현의 존재만으로 advisory를 만들지 않습니다.

다만 같은 가이드 안의 충돌, `guides/`가 `AGENTS.md` 또는 `rules/`보다 우선한다고 오해하게 만드는 설명, 예시·재사용 패턴을 Hard Rule처럼 서술한 경우, 실제 rule 또는 harness 정책과의 명백한 모순, 행동 차이를 만드는 모호성, 특정 implementation을 범용 의무로 과도하게 처방한 경우에는 advisory 대상이 될 수 있습니다.

### 📋 진단 체크리스트 (Advisory Rubric)

1. **상호 충돌 (Conflict) 진단**:
   * 최상위 헌법 모듈(`01-base.md`)과 하위 규칙, 또는 가이드와 실제 rule/harness 정책이 정면으로 충돌하는가?
2. **의미적 모호성 (Ambiguity) 진단**:
   * 여러 합리적 해석이 실제 행동 차이를 만들며, scope·authority·조건을 불명확하게 하는가?
3. **실효성 및 중복 (Redundancy) 진단**:
   * 서로 다른 규칙 모듈 간 동일한 지시가 불필요하게 반복되거나, 목적을 흐리는가?
4. **아티팩트 격리 (Isolation) 진단**:
   * 내부 메타(`/.agents/`)가 외부 배포 자산으로 유출되었거나, `guides/`가 규범 문서로 오해되게 배치되었는가?
5. **오버엔지니어링 & ROI (Over-engineering & Value) 진단**:
   * 특정 implementation을 범용 의무로 고정하거나, 작업 위험보다 과도한 규칙·skill·subagent 절차를 요구하는가?

의미 진단은 예외 조항의 조건 누락, 여러 기본값의 우선순위 부재, 목적보다 구현을 고정하는 처방, 필수·권고 강도의 혼동, 의미상 적용 범위의 불명확성을 권고로 보고할 수 있습니다. 단일 키워드 존재만으로 오류나 권고를 만들지 않으며, 문맥과 실제 충돌 가능성을 확인합니다.

> 📢 **진단 보고 프로토콜**:
> Phase 2 진단 결과는 빌드를 차단하는 Error가 아닌 **'권고 보고서(Advisory Report)'** 형태로 사용자에게 제시하며, 사용자의 승인을 얻은 후에만 가이드를 반영합니다.
