# AGENTS.md - Agents Template & Shared Standard

본 문서는 `agents-template` 프로젝트에서 작업하는 모든 AI 에이전트(Agentic AI)가 반드시 준수해야 하는 **최상위 실행 규칙 및 프로젝트 헌법(Constitution)** 지침입니다.

---

## 🏛️ 1. 프로젝트 헌법 (Core Principles)

### I. Universal Compatibility & Standardization (범용성 및 표준화)
모든 공용 `AGENTS.md` 규격 및 모듈은 특정 AI 에이전트(Antigravity, Cursor, Claude Code, Windsurf 등)나 언어/프레임워크에 귀속되지 않고 범용적으로 적용될 수 있도록 가이드라인과 템플릿 표준을 준수해야 합니다.

### II. Strict Execution Control & Procedural Integrity (엄격한 실행 제어 및 절차적 무결성)
에이전트의 안정적 운영 및 예측 가능성을 위해 사전 승인 절차(Strict Execution Control), 자율 수정 제한, 질의응답 대기 규칙, 보안 규칙을 기본적이고 불변하는 규칙으로 명시해야 합니다.

### III. Modular Composition & Extensibility (모듈화 및 확장성)
규칙은 Global Base, Workflow, Tool Guidelines, Tech Stack Specific Rules 등의 독립된 모듈 단위로 작성되며, 대상 프로젝트의 요구사항에 맞게 자유롭게 조합 및 확장할 수 있어야 합니다.

### IV. Semantic Versioning & Traceability (버전 관리 및 추적 가능성)
공용 `AGENTS.md` 모듈 및 완성본 파일은 시맨틱 버저닝(MAJOR.MINOR.PATCH) 규격을 따르며, 헌법 및 모듈 개정 시 개정 이유와 변경 이력을 명확히 추적할 수 있도록 명시해야 합니다.

### V. LLM-Driven Generation & Validation (LLM 기반 생태계 조립 및 검증)
AI 에이전트는 규칙 모듈 개정 시 자동 조립 스크립트(`scripts/build_dist.py`) 및 무결성 검증 도구를 호출하여 `dist/` 배포 아티팩트를 100% 최신화하고 검증 체계를 유지해야 합니다.

### VI. Isolation of Internal vs Distributable Artifacts (내부 및 배포 아티팩트의 엄격한 격리)
1. **내부 전용 (`.agents/`)**: 이 레포지토리 자체의 개발·유지보수를 위한 메타 스킬과 내부 서브에이전트는 `.agents/` 디렉터리 내에서만 관리되며, 절대 `dist/` 배포 아티팩트에 포함되지 않는다.
2. **외부 배포용 (`rules/`, `skills/`, `subagents/` ➔ `dist/`)**: 타 프로젝트로 배포될 모든 공용 규칙, 스킬, 서브에이전트는 루트의 `rules/`, `skills/`, `subagents/` 원본에서 관리되며, `scripts/build_dist.py` 스크립트를 통해서만 `dist/` 아티팩트로 조립 배포된다.

---

## ⚡ 2. 최상위 실행 통제 수칙 (Core Operational Rules)

### 2.1 언어 및 커뮤니케이션 (Language & Communication)
- **한국어 최우선**: 모든 대화, 문서화, 커밋 메시지는 한국어를 기본으로 사용합니다. (단, 코드 내 식별자, 기술 용어, 파일 경로는 원문 유지)
- **스킬 고지**: 스킬(`activate_skill` 등)을 활용할 때는 어떤 전문성과 목적을 위해 스킬을 사용하는지 사용자에게 명시적으로 알립니다.

### 2.2 엄격한 실행 제어 (Strict Execution Control)
- **사전 승인 필수**: 사용자가 명시적으로 파일 수정, 삭제, 쉘 명령 실행을 명령하지 않은 경우, 실행 전에 변경될 내용(Diff 또는 명령어)과 예상되는 영향을 요약 제시하고 사용자의 명시적인 승인(`진행해`, `Go`, `승인`)을 얻은 후 진행합니다.
- **질문-답변-대기**: 사용자가 질문이나 의문 사항을 제시한 경우, 답변 직후 임의로 다음 단계(파일 수정 등)로 넘어가거나 도구를 호출하지 않고 사용자의 추가 지시를 철저히 대기합니다.
- **모호성 해소 후 구현**: 요구사항이 불명확할 때는 지레짐작 코딩을 금지하며, 질문과 함께 합리적 기본값(Default Option)을 제시하고 필요한 경우 질문을 1회로 묶어(Batched Questions) 확인받은 후 구현에 진입합니다.
- **독단적 판단 금지**: "수정하겠습니다"라고 즉시 도구를 호출하지 말고, 제안 및 내용을 먼저 보고한 후 멈춰 섭니다.
- **명시적 지시(Directive) 시 즉시 실행**: 사용자가 "커밋해", "파일 생성해", "테스트 실행해"와 같이 결과가 명확한 direct 명령을 내린 경우 별도의 추가 승인 절차 없이 즉시 수행합니다.

### 2.3 출력 무결성 원칙 (Output Integrity Principle)
- **무단 요약 및 생략 절대 금지**: 파일 작성이나 수정 시 지정된 부분을 제외한 원본의 전후 문맥 및 인접 항목은 단 한 글자도 누락 없이 100% 원본과 동일하게 유지해야 합니다.
- **금지 표현 (Zero Tolerance)**:
  - `... (중략) ...`
  - `// 기존 내용과 동일`
  - `[나머지 부분 생략]`
  - `(이전 코드는 위와 같음)`
- **부분 수정 권장**: 전체 파일을 새로 쓰는 대신 변경이 필요한 부분만 안전하게 수정하는 방식을 우선시합니다.

### 2.4 환경, 보안 & OS 호환성 (Environment, Security & OS Compatibility)
- **인코딩 표준**: 모든 파일 읽기 및 쓰기 작업은 `UTF-8` 인코딩을 기준으로 수행하여 한글 깨짐을 방지합니다.
- **자격 증명 보호**: 코드, 스크립트, 문서 내에 API 키, 비밀번호, 토큰 등 민감 정보를 절대로 하드코딩하지 않으며 환경 변수(`.env`) 처리를 기본으로 합니다.
- **OS 및 터미널 호환성**: Windows(PowerShell 5.1) 및 범용 터미널 환경을 고려하여 OS 종속적인 명령어(`&&` 대신 `;`, 특정 터미널 세션 등)의 사용을 지양하고 에이전트 내장 비동기 도구를 우선 활용합니다.

### 2.5 패키지 및 의존성 관리 원칙 (Dependency & Package Policy)
- **최소 의존성 및 자체 구현 우선 (In-House First)**: 100줄 이내의 단순 유틸리티나 프레임워크 내장 기능(예: Auth, ORM, State)으로 구현 가능한 항목은 외부 패키지 설치 없이 자체 구현하여 의존성 오염을 방지합니다.
- **패키지 건전성 평가 (Package Health Check)**: 신규 패키지 도입 시 유지보수 활성화, 커뮤니티 평판, 상용 호환 라이선스(MIT/Apache 등), 전이적 의존성 유입 여부를 사전 검증하고 사용자 승인을 얻어 설치합니다.

### 2.6 세션 인계 및 자가 치유 (Handoff & Self-Healing)
- **세션 맥락 인계 (`HANDOFF.md`)**: 세션 리셋, 맥락 압축, 또는 에이전트 전환 시 목표·시도 내역·성공/실패 원인·다음 단계를 `HANDOFF.md`에 정밀 기록하여 연속성을 유지합니다.
- **조건부 자가 치유 루프**: 단순 린터/타입 오류는 AI가 스스로 수정하되, 논리적 테스트 실패 시 무한 재시도하지 않고 사용자에게 원인을 분석 보고 후 승인을 대기합니다.

---

## 📂 3. 프로젝트 구조 및 모듈 아키텍처 (Project Structure & Modules)

```text
agents-template/
├── rules/                   # 📌 SSOT: 규칙 원본 모듈 (단 1회만 정의되는 원본)
│   ├── core/                # 🎯 공용 핵심 규칙 모듈
│   │   ├── 01-base.md       # 진실의 계층, 기계적 하네스, 보안, 정직성
│   │   ├── 02-workflow.md   # 5단계 행동 프로토콜, 자가치유, 승인 절차
│   │   ├── 03-integrity.md  # 출력 무결성 원칙, 금지 표현
│   │   ├── 04-standards.md  # 코딩, 의미 있는 테스트 및 커밋 메시지 표준
│   │   └── 05-docs-maintenance.md # 지속적 문서 관리 및 CHANGELOG 동기화
│   ├── architecture/        # 🏛️ 도메인 및 아키텍처 규칙 모듈
│   │   ├── web-frontend.md  # 웹 프론트엔드 특화 지침
│   │   ├── backend-api.md   # 백엔드 API 특화 지침
│   │   ├── database-orm.md  # 범용 DB 마이그레이션 & ORM 안전 지침
│   │   ├── library-package.md # 범용 라이브러리 및 패키지 의사결정 지침
│   │   └── monorepo.md      # 모노레포 아키텍처 특화 지침
│   ├── frameworks/          # 🛠️ 프레임워크 특화 규칙 모듈
│   │   ├── django.md        # Django 프레임워크 특화 지침
│   │   ├── react.md         # React.js SPA 특화 지침
│   │   ├── next.md          # Next.js App Router / SSR 특화 지침
│   │   ├── vue.md           # Vue 3 Composition API / Pinia 특화 지침
│   │   ├── nuxt.md          # Nuxt 3 SSR / Nitro Engine 특화 지침
│   │   ├── fastapi.md       # FastAPI Pydantic v2 / DI 특화 지침
│   │   └── litestar.md      # Litestar DTO / ASGI 특화 지침
│   ├── packaging/           # 📦 패키징 및 배포 생태계 규칙 모듈
│   │   ├── package-npm.md   # Node.js / TypeScript NPM 패키징 지침
│   │   ├── package-python.md# Python / PyPI 패키징 지침
│   │   ├── docker.md        # Docker Multi-stage & 컨테이너 최적화 지침
│   │   ├── deployment-nginx.md # Nginx Reverse Proxy & 보안 지침
│   │   └── deployment-python-server.md # Gunicorn + Uvicorn 배포 프로세스 지침
│   └── styles/              # 🎨 언어별 코딩 스타일 가이드 모듈
│       ├── python.md        # Python 코딩 스타일 지침 (Google Style Guide)
│       ├── typescript.md    # TypeScript 코딩 스타일 지침 (Google Style Guide)
│       ├── javascript.md    # JavaScript 코딩 스타일 지침 (Google Style Guide)
│       ├── html-css.md      # HTML/CSS 코딩 스타일 지침 (Google Style Guide)
│       ├── go.md            # Go 코딩 스타일 지침 (Effective Go)
│       ├── cpp.md           # C++ 코딩 스타일 지침 (Google Style Guide)
│       ├── csharp.md        # C# 코딩 스타일 지침 (Google Style Guide)
│       └── dart.md          # Dart/Flutter 코딩 스타일 지침 (Effective Dart)
├── skills/                  # 🚀 배포용 공용 에이전트 스킬 원본 모듈 (SSOT)
│   ├── gitignore-generator/ # 언어/프레임워크별 .gitignore 최적화 자동 생성 스킬
│   └── handoff/             # 세션 맥락 인계 및 HANDOFF.md 자동 생성 스킬
├── subagents/               # 🚀 배포용 공용 서브에이전트 원본 모듈 (SSOT)
│   └── critical-evaluator.md# 코드 및 설계 변경사항 비판적 검증 서브에이전트
├── .agents/                 # 🔒 이 프로젝트 전용 메타 스킬 및 서브에이전트 (배포 안 됨)
│   ├── skills/              # 메타 스킬 (rule-validator: 룰셋 무결성 정적 검증)
│   └── agents/              # 메타 서브에이전트 (critical-evaluator)
├── scripts/                 # 🛠️ 자동 조립 파이썬 스크립트
│   └── build_dist.py        # dist/ 배포 아티팩트 자동 조립 도구
├── dist/                    # 📦 배포용 아티팩트 디렉터리 (Git 트래킹 및 CI 배포)
│   ├── AGENTS.md            # 필수 핵심 규칙이 번들링된 통합 배포 파일
│   ├── rules/               # 온디맨드 기술 스택/스타일 규칙 모듈
│   └── .agents/             # 🎯 Target 프로젝트 루트용 자동 호환 배포 디렉터리
│       ├── skills/          # dist/.agents/skills/
│       └── agents/          # dist/.agents/agents/
├── AGENTS.md                # 최상위 실행 지침 및 프로젝트 헌법 (Constitution)
├── README.md                # 프로젝트 안내 문서
├── CHANGELOG.md             # 프로젝트 개정 및 버전 이력 문서
└── LICENSE.md               # MIT 라이선스
```

---

## 📜 4. 거버넌스 및 지속적 문서 관리 (Governance & Documentation)

### 4.1 거버넌스 & Git 커밋 규약
- **프로젝트 헌법 규범**: 본 문서는 프로젝트의 최상위 규범이며 헌법 개정 시 시맨틱 버저닝을 동반합니다.
- **Conventional Commits 준수**: 커밋 메시지는 Conventional Commits 규격(`feat:`, `fix:`, `docs:` 등)을 준수하고 "Why"에 집중하여 작성합니다.
- **원자적 커밋 및 분할 커밋 수칙**: 하나의 작업 트랜잭션(원본 수정, 문서 최신화, `dist/` 빌드)은 정합성을 위해 단일 원자적 커밋으로 유지하되, 목적이 서로 완벽히 무관한 2개 이상의 별개 이슈를 작업한 경우에만 이슈별로 커밋을 분할합니다.
- **AI Attribution 노이즈 제어**: AI 도구가 커밋/PR에 자동 추가하는 서명 링크 노이즈는 개발 환경 설정을 통해 사전에 정리하도록 권장합니다.

### 4.2 지속적 문서 관리 및 CHANGELOG 동기화
- **Doc-Code 동기화 원칙**: 주요 기능 추가, 아키텍처 개정, CLI/환경 설정 변경 시 기존 문서(README.md, AGENTS.md 등)를 수술적 편집(Surgical Edit)으로 동기화하여 문서 부채(Documentation Debt)를 방지합니다.
- **CHANGELOG.md 개정 의무**: 의미 있는 기능 추가, 모듈 구조 변경, Breaking Changes 발생 시 [CHANGELOG.md](file:///CHANGELOG.md)에 시맨틱 버저닝 기준에 따라 개정 내역을 지속 기록합니다.
- **신규 문서 사전 승인 (Ask Before Create)**: 프로젝트 내 존재하지 않는 신규 문서를 생성해야 할 경우 임의 생성하지 않고 사용자에게 사전 필요성을 설명하고 승인을 얻어 생성합니다.

### 4.3 단순성 추구 및 우선순위 (Hierarchy of Truth)
- **오버엔지니어링 경계**: 불필요한 규칙 양산과 과도한 레이어 추가를 경계하며, 비효율적인 지시에는 대안을 제안(Push Back)합니다.
- **판단 우선순위**: 규칙 간 충돌 시 `실제 로컬 코드/컨텍스트 > 프로젝트 설정 > AGENTS.md`의 우선순위를 따릅니다.

---

**Version**: 1.1.0 | **Ratified**: 2026-07-24 | **Last Amended**: 2026-08-01
