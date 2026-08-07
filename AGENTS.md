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
- **내부 전용 (`.agents/`)**: 이 레포지토리 루트의 내부 전용 메타 자산은 `dist/`에 직접 복사되지 않고 레포지토리 메타 유지보수에만 사용됩니다.
- **외부 배포용 (`rules/`, `skills/`, `subagents/`)**: 타 프로젝트로 배포될 공용 규칙, 스킬, 서브에이전트는 `scripts/build_dist.py` 스크립트를 통해서만 `dist/` 아티팩트로 조립·배포됩니다.

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
├── skills/                  # 🚀 배포용 공용 스킬 (gitignore-generator, handoff, python-ecosystem-kb)
├── subagents/               # 🚀 배포용 공용 서브에이전트 (auditor.md)
├── .agents/                 # 🔒 이 프로젝트 전용 메타 자산 (rule-validator, auditor.md)
├── scripts/                 # 🛠️ 자동 빌드 스크립트 (build_dist.py)
└── dist/                    # 📦 자동 조립 배포 아티팩트 (AGENTS.md, rules/, .agents/)
```

---

## 📜 5. 배포 자산 관리 & 지속적 동기화

- 공용 규칙, 스킬, 서브에이전트 변경 시 `python scripts/build_dist.py`를 실행하여 `dist/` 배포 아티팩트를 100% 최신화합니다.
- 정적 검증 도구(`python .agents/skills/rule-validator/scripts/validate_rules.py`)를 통해 규칙 무결성을 검증합니다.
- **문서화 및 커밋 언어**: 커밋 메시지의 구조적 키워드(`feat`, `fix`, `docs`, `refactor` 등)는 영어 표준 형식을 사용하고 설명과 본문은 명시된 프로젝트 언어를 우선합니다. 프로젝트 언어가 없으면 사용자의 주 언어를 따릅니다. Docstring과 주석은 기존 프로젝트 관례를 유지하며, LLM 에이전트는 별도 지시 없이 문서화 언어를 임의로 변경하지 않습니다.
- **원자적·논리적 분할 커밋**: 하나의 작업 이슈에 속하는 코드, 테스트, 문서와 생성 아티팩트는 함께 커밋합니다. 목적·영향 범위·검증 근거가 독립적인 변경은 별도 커밋으로 분리합니다.

---

**Version**: 2.0.0 | **Ratified**: 2026-08-05 | **Architecture**: Modern Planning-First, Risk-Proportional Harness
