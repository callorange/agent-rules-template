# AGENTS.md - Agents Template & Shared Standard

본 문서는 `agents-template` 프로젝트 및 이 템플릿을 사용하는 프로젝트에서 작업하는 모든 AI 에이전트가 준수해야 하는 **최상위 실행 지침 및 프로젝트 헌법(Constitution)**입니다.

---

## 🏛️ 1. 프로젝트 헌법 (Core Principles)

### I. Universal Compatibility & Standardization (범용성 및 표준화)
모든 규칙 및 스킬/서브에이전트 모듈은 특정 AI 플랫폼이나 언어/프레임워크에 귀속되지 않고 범용적으로 적용 가능하도록 가이드라인과 템플릿 표준을 준수합니다.

### II. Hierarchy of Truth (진실의 계층 및 우선순위)
규칙 간 충돌이나 모호성이 발생할 경우 다음 우선순위를 절대적으로 적용합니다.
1. **플랫폼·시스템 지침 및 법적·보안 제약** (비밀값 보호, 시스템 권한 경계)
2. **사용자의 대화 창 직접 지시** (User Directives)
3. **프로젝트별 환경 설정 및 지침** (`package.json`, `.eslintrc`, 프로젝트 전용 헌법)
4. **공용 규칙 모듈 및 기본 지침** (`AGENTS.md`, `rules/*.md`)

### III. Isolation of Internal vs Distributable Artifacts (내부 및 배포 자산의 엄격한 격리)
- **내부 전용 (`.agents/`)**: 이 레포지토리 루트의 내부 전용 메타 자산은 bundle에 직접 복사되지 않고 레포지토리 메타 유지보수에만 사용됩니다.
- **외부 배포용 (`rules/`, `guides/`, `skills/`, `subagents/`)**: 타 프로젝트로 배포될 공용 자산은 `scripts/build_dist.py`를 통해서만 `agent_rules_template/bundle/`로 조립·배포됩니다. 이 중 `guides/`는 규칙을 설계·검토할 때 선택적으로 참조하는 비규범적 자료이며, `AGENTS.md` 또는 `rules/`보다 우선하지 않고 일반 작업에 자동 적용되지 않습니다.

### IV. Harness Change Principles (하네스 변경 원칙)
- 하네스는 목적·제약·안전 경계와 검증 가능한 품질을 명확히 하기 위해 사용합니다.
- 규칙이나 절차를 추가·강화하기 전에는 해결하려는 구체적 실패 사례와, 그 통제가 실패 비용을 실질적으로 낮추는 근거를 확인합니다.
- 안전, 권한, 법적 제약, 비가역적 변경 또는 기계적으로 검증 가능한 품질 기준은 유지하거나 강화합니다.
- 특정 실행 순서, 반복 검토, 다중 에이전트 분업, 모델별 우회책은 필요성과 효과가 입증될 때만 적용합니다.
- 단순하고 가역적인 작업에는 최소한의 정보 확인과 검증만 요구합니다.
- 더 나은 모델 성능이나 도구로 기존 규칙의 필요성이 사라지면, 해당 규칙을 제거하거나 선택 사항으로 전환합니다.

---

## 🛡️ 2. 안전 경계 & 정량적 검증 (Safety Boundaries & Validation)

### 2.1 위험 기반 안전 경계 (Safety Boundaries)
- **자율 실행 (Read-only & Reversible)**: 코드 읽기, 검색, 가역적 로컬 코드 수정, 격리된 테스트 실행은 추가 승인 없이 자율적으로 수행합니다.
- **사전 승인 필수 (High-risk Side-effects)**: 파일 영구 삭제, 외부 전송/비용 발생, 자격 증명 변경, 실제 공유/운영 환경 반영은 실행 전 위험도와 변경 내역을 요약 보고하고 사용자 승인을 얻습니다.
- **보안 및 인코딩**: 자격 증명(API 키, 토큰) 노출 금지(환경 변수 및 `.env` 활용), Windows 작업 시 UTF-8 인코딩 기본 적용.

### 2.2 증거 기반 검증 (Evidence-Based Validation)
- 하네스는 목적·제약·안전 경계와 검증 가능한 품질을 명확히 하는 데 사용합니다. 특정 실행 순서나 반복 검토는 실제 위험을 낮추거나 기계적으로 검증 가능한 경우에만 적용합니다.
- 에이전트 스스로 코드의 정확성을 정성적으로 추측하지 말고, Linter, Type Checker, Test Runner, 빌드 스크립트 등 **정량적 검증 도구**를 호출하여 결과를 확인합니다.

---

## 🎯 3. 기획 계약 (Planning Contract)

복잡하거나 파괴적인 작업, 다수의 선택지가 존재하는 경우에만 구현에 앞서 다음 기획 하네스를 정렬합니다. 단순하고 가역적인 작업에는 필요한 정보 확인과 최소 검증만 적용합니다.
1. **목적 및 성공 기준 (What & Why)**: 해결하려는 문제와 기대하는 구체적 성과 명시.
2. **판단 기준과 제약 (Trade-offs)**: 의사결정 우선순위(예: "속도보다 정확성 우선") 및 넘지 말아야 할 선 설정.
3. **의사결정 기록 (ADR)**: 중대한 아키텍처나 되돌리기 어려운 결정은 사유와 버린 대안을 간략히 기록.

---

## 📂 4. 프로젝트 구조 및 모듈 아키텍처 (Project Structure)

```text
agents-template/
├── AGENTS.md                # 최상위 실행 지침 및 프로젝트 헌법 (Constitution)
├── rules/                   # 📌 온디맨드 공용 규칙 원본 모듈 (SSOT)
│   ├── core/                # 핵심 기본 규칙 (01-base, 02-workflow, 03-integrity, 04-standards, 05-docs-maintenance)
│   ├── architecture/        # 아키텍처 지침 (web-frontend, backend-api, database-orm, monorepo 등)
│   ├── frameworks/          # 프레임워크 지침 (django, react, next, vue, fastapi, litestar 등)
│   ├── packaging/           # 배포/패키징 지침 (docker, deployment, package-npm, package-python 등)
│   └── styles/              # 코딩 스타일 가이드 (python, typescript, javascript, go, cpp, csharp, dart 등)
├── guides/                  # 📚 선택형 비규범적 설계 참고 자료 (prompt/context/task contract/harness)
├── skills/                  # 🚀 배포용 공용 스킬 (gitignore-generator, handoff, python-ecosystem-kb)
├── subagents/               # 🚀 배포용 공용 서브에이전트 (auditor.md)
├── .agents/                 # 🔒 이 프로젝트 전용 메타 자산 (rule-validator, auditor.md)
├── scripts/                 # 🛠️ 자동 빌드 스크립트 (build_dist.py)
└── agent_rules_template/bundle/ # 📦 자동 조립 배포 아티팩트
```

---

## 📜 5. 배포 자산 관리 & 지속적 동기화

### 배포 아티팩트 동기화

- `rules/`, `guides/`, `skills/`, `subagents/`의 배포 대상 원본이 변경되면 `python scripts/build_dist.py`를 실행합니다.
- build 후 `agent_rules_template/bundle/`과 `metadata.json`이 현재 원본을 반영하는지 검증합니다.
- 소비 프로젝트에는 source를 직접 복사하지 않고 `agent-rules`가 bundle 및 ownership metadata를 기준으로 설치·업데이트합니다.

### 배포 버전 정책

다음 중 하나가 확인되면 현재 작업에서 배포 버전을 한 번 올립니다.

- `rules/`, `guides/`, `skills/`, `subagents/` 변경으로 소비 프로젝트에 설치되는 내용 또는 에이전트가 따라야 할 규범적 동작이 바뀜
- `agent-rules`의 CLI, sync, migration, ownership, metadata, 설치·업데이트 동작 또는 소비 프로젝트와의 계약이 바뀜

다음 변경만 있는 경우에는 배포 버전을 올리지 않습니다.

- 테스트 또는 CI만 변경
- 저장소 내부 문서만 변경
- 코드 주석 또는 포맷팅만 변경
- 소비 프로젝트의 bundle 내용, 규범적 동작, 설치·업데이트 계약에 영향을 주지 않는 내부 구현 변경

버전 단계는 변경의 호환성 영향으로 결정합니다.

- **major**: 기존 소비 프로젝트가 수동 변경 없이 기존 설치·업데이트 계약 또는 공개된 사용 방식을 계속 사용할 수 없는 변경
- **minor**: 기존 계약을 유지하면서 새 기능·규칙·가이드·스킬·서브에이전트·CLI 기능을 추가하거나, 소비 프로젝트 또는 에이전트의 규범적 동작을 변경하는 하위 호환 변경
- **patch**: 기존 계약과 규범적 동작을 유지하는 버그 수정, 오탈자·표현 명확화, 패키징·metadata·내부 구현 수정

한 작업에 여러 종류의 변경이 포함되면 파일별로 버전을 올리지 않고, 해당 작업에 필요한 가장 높은 단계로 한 번만 올립니다.

버전을 올릴 때는 루트 `AGENTS.md`의 `Version`을 기준으로 다음을 같은 변경에서 동기화합니다.

- `AGENTS.md`
- `pyproject.toml`
- `README.md`
- `CHANGELOG.md`
- `python scripts/build_dist.py`가 생성하는 `agent_rules_template/bundle/metadata.json`

build 후 `bundle/metadata.json`의 `template_version`이 루트 `AGENTS.md`의 버전과 일치하는지 확인합니다.

### 검증

- 규칙 원본 또는 배포 bundle이 변경되면 `python .agents/skills/rule-validator/scripts/validate_rules.py`를 실행하여 규칙 무결성을 검증합니다.
- 코드·sync·패키징 동작이 변경되면 해당 변경을 직접 검증하는 테스트와 build를 함께 실행합니다.
- 검증을 실행하지 못했거나 실패한 경우 성공으로 보고하지 않고 원인과 미검증 범위를 명시합니다.

### 소통·문서화 및 커밋 언어

소통, 문서화, 커밋 언어는 서로 독립적으로 결정하며 사용자의 명시적 지시를 프로젝트 기본값보다 우선합니다.

- **소통**: 명시적 지시 → 현재 자연어 요청 → 요청이 불명확하면 최근 직접 메시지 → 프로젝트 기본값 → 기존 관례 순으로 결정합니다. 별도 기준이 없으면 현재 요청 언어를 사용합니다.
- **문서화**: 명시적 문서화 지시 → 프로젝트 설정 → 현재 요청 언어 → 기존 관례 순으로 결정합니다. 별도 기준이 없으면 새 규칙·자연어 설명·Docstring·주석은 한국어를 기본값으로 사용합니다.
- **기존 문서**: 명시적인 번역 또는 언어 변경 요청이 없으면 기존 언어를 보존합니다.
- **기술 표현**: 기술 고유명사, 식별자, 표준 섹션명, 코드 블록, 명령, 파일명, API 식별자는 필요한 경우 영어를 유지합니다.
- **커밋**: Conventional Commit 타입(`feat`, `fix`, `docs`, `refactor` 등)은 영어로 유지합니다. 제목 설명과 본문은 명시적 커밋 지시 → 프로젝트 설정 → 일관된 기존 커밋 관례 → 현재 요청 언어 → 에이전트 기본값 순으로 결정합니다. 별도 기준이 없으면 `<type>: <한국어 설명>`과 한국어 본문을 사용합니다.
- 문서화 또는 커밋 언어 설정을 소통 언어로 전파하지 않습니다.
- 이름, 위치, OS locale, 코드 또는 모델 기본값을 언어 판단 근거로 사용하지 않습니다.

### 커밋 분할

- 하나의 작업 이슈에 속하고 함께 검증되는 코드, 테스트, 문서, 버전 정보 및 생성 아티팩트는 같은 논리적 커밋에 포함합니다.
- 목적, 영향 범위 또는 검증 근거가 독립적인 변경은 별도 커밋으로 분리합니다.

---

## 🧭 6. 온디맨드 규칙 활성화 계약

- 작업 대상에 따른 필수 모듈 선택, 누적 적용 및 충돌 우선순위는 [Core 온디맨드 규칙 활성화 계약](rules/core/01-base.md#-2-온디맨드-규칙-활성화-계약)을 따릅니다.
- 소비 프로젝트는 [README의 활성화 템플릿과 설정 체크리스트](README.md)를 바탕으로 경로·기술 스택·public 범위·문서화 언어·자동 검사 범위를 자체 `AGENTS.md`와 설정에서 확정합니다.

---

**Version**: 2.4.0 | **Ratified**: 2026-08-05 | **Architecture**: Modern Planning-First, Risk-Proportional Harness
