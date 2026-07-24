# AGENTS.md - Agents Template & Shared Standard

본 문서는 `agents-template` 프로젝트에서 작업하는 모든 AI 에이전트(Agentic AI)가 반드시 준수해야 하는 **최상위 실행 규칙 및 프로젝트 헌법(Constitution)** 지침입니다.

---

## 🏛️ 프로젝트 헌법 (Core Principles)

### I. Universal Compatibility & Standardization (범용성 및 표준화)
모든 공용 `AGENTS.md` 규격 및 모듈은 특정 AI 에이전트(Antigravity, Cursor, Claude Code, Windsurf 등)나 언어/프레임워크에 귀속되지 않고 범용적으로 적용될 수 있도록 가이드라인과 템플릿 표준을 준수해야 합니다.

### II. Strict Execution Control & Procedural Integrity (엄격한 실행 제어 및 절차적 무결성)
에이전트의 안정적 운영 및 예측 가능성을 위해 사전 승인 절차(Strict Execution Control), 자율 수정 제한, 질의응답 대기 규칙, 보안 규칙을 기본적이고 불변하는 규칙으로 명시해야 합니다.

### III. Modular Composition & Extensibility (모듈화 및 확장성)
규칙은 Global Base, Workflow, Tool Guidelines, Tech Stack Specific Rules 등의 독립된 모듈 단위로 작성되며, 대상 프로젝트의 요구사항에 맞게 자유롭게 조합 및 확장할 수 있어야 합니다.

### IV. Semantic Versioning & Traceability (버전 관리 및 추적 가능성)
공용 `AGENTS.md` 모듈 및 완성본 파일은 시맨틱 버저닝(MAJOR.MINOR.PATCH) 규격을 따르며, 헌법 및 모듈 개정 시 개정 이유와 변경 이력을 명확히 추적할 수 있도록 명시해야 합니다.

### V. LLM-Driven Generation & Validation (LLM 직접 생성 및 검증)
외부 스크립트에 의존하지 않고 AI 에이전트(LLM)가 스킬 지침을 기반으로 직접 규칙을 조합하여 `dist/`에 생성하고 검증 체계를 유지해야 합니다.

---

## 📂 프로젝트 구조 (Project Structure)

```text
agents-template/
├── rules/                   # 📌 SSOT: 규칙 원본 모듈 (단 1회만 정의되는 원본)
│   ├── core/                # 🎯 공용 핵심 규칙 모듈
│   │   ├── base.md          # 진실의 계층, 기계적 하네스, 보안, 정직성
│   │   ├── workflow.md      # 5단계 행동 프로토콜, 자가치유, 승인 절차
│   │   ├── integrity.md     # 출력 무결성 원칙, 금지 표현
│   │   ├── standards.md     # 코딩 및 커밋 메시지 표준
│   │   └── hidden-knowledge.md # 암묵적 지식 템플릿
│   ├── architecture/        # 🏛️ 도메인 및 아키텍처 규칙 모듈
│   │   ├── web-frontend.md  # 웹 프론트엔드 특화 지침
│   │   ├── backend-api.md   # 백엔드 API 특화 지침
│   │   ├── framework-django.md # Django 프레임워크 특화 아키텍처 지침
│   │   ├── library-package.md # 범용 라이브러리/모듈 공통 지침
│   │   └── monorepo.md      # 모노레포 아키텍처 특화 지침
│   ├── packaging/           # 📦 패키징 및 배포 생태계 규칙 모듈
│   │   ├── package-npm.md   # Node.js / TypeScript NPM 패키징 지침
│   │   └── package-python.md# Python / PyPI 패키징 지침
│   └── styles/              # 🎨 언어별 코딩 스타일 가이드 모듈
│       ├── python.md        # Python 코딩 스타일 지침 (Google Style Guide)
│       ├── typescript.md    # TypeScript 코딩 스타일 지침 (Google Style Guide)
│       ├── javascript.md    # JavaScript 코딩 스타일 지침 (Google Style Guide)
│       ├── html-css.md      # HTML/CSS 코딩 스타일 지침 (Google Style Guide)
│       ├── go.md            # Go 코딩 스타일 지침 (Effective Go)
│       ├── cpp.md           # C++ 코딩 스타일 지침 (Google Style Guide)
│       ├── csharp.md        # C# 코딩 스타일 지침 (Google Style Guide)
│       └── dart.md          # Dart/Flutter 코딩 스타일 지침 (Effective Dart)
├── dist/                    # AI 에이전트(LLM)가 직접 조립해 생성하는 출력 디렉토리
│   └── AGENTS.md            # 최종 조합 완료된 AGENTS.md
├── AGENTS.md                # 최상위 실행 지침 및 프로젝트 헌법 (Constitution)
├── README.md                # 프로젝트 안내 문서
└── LICENSE.md               # MIT 라이선스
```

---

## 1. 언어 및 커뮤니케이션 (Language & Communication)

- **한국어 최우선**: 모든 대화, 문서화, 커밋 메시지는 한국어를 기본으로 사용합니다. (단, 코드 내 식별자, 기술 용어, 파일 경로는 원문 유지)
- **스킬 고지**: 스킬(`activate_skill` 등)을 활용할 때는 어떤 전문성과 목적을 위해 스킬을 사용하는지 사용자에게 명시적으로 알립니다.

---

## 2. 엄격한 실행 제어 (Strict Execution Control)

- **사전 승인 필수**: 사용자가 명시적으로 파일 수정, 삭제, 쉘 명령 실행을 명령하지 않은 경우, 실행 전에 변경될 내용(Diff 또는 명령어)과 예상되는 영향을 요약 제시하고 사용자의 명시적인 승인(`진행해`, `Go`, `승인`)을 얻은 후 진행합니다.
- **질문-답변-대기**: 사용자가 질문이나 의문 사항을 제시한 경우, 답변 직후 임의로 다음 단계(파일 수정 등)로 넘어가거나 도구를 호출하지 않고 사용자의 추가 지시를 철저히 대기합니다.
- **독단적 판단 금지**: "수정하겠습니다"라고 즉시 도구를 호출하지 말고, 제안 및 내용을 먼저 보고한 후 멈춰 섭니다.
- **명시적 지시(Directive) 시 즉시 실행**: 사용자가 "커밋해", "파일 생성해", "테스트 실행해"와 같이 결과가 명확한 direct 명령을 내린 경우 별도의 추가 승인 절차 없이 즉시 수행합니다.

---

## 3. 출력 무결성 원칙 (Output Integrity Principle)

- **무단 요약 및 생략 절대 금지**: 파일 작성이나 수정 시 지정된 부분을 제외한 원본의 전후 문맥 및 인접 항목은 단 한 글자도 누락 없이 100% 원본과 동일하게 유지해야 합니다.
- **금지 표현 (Zero Tolerance)**:
  - `... (중략) ...`
  - `// 기존 내용과 동일`
  - `[나머지 부분 생략]`
  - `(이전 코드는 위와 같음)`
- **부분 수정 권장**: 전체 파일을 새로 쓰는 대신 변경이 필요한 부분만 안전하게 수정하는 방식을 우선시합니다.

---

## 4. 환경 및 보안 (Environment & Security)

- **인코딩 표준**: 모든 파일 읽기 및 쓰기 작업은 `UTF-8` 인코딩을 기준으로 수행하여 한글 깨짐을 방지합니다.
- **자격 증명 보호**: 코드, 스크립트, 문서 내에 API 키, 비밀번호, 토큰 등 민감 정보를 절대로 하드코딩하지 않으며 환경 변수(`.env`) 처리를 기본으로 합니다.

---

## 5. 에러 처리 및 디버깅 (Error Handling)

- **무단 재시도 금지**: 명령 실행이나 테스트 실패 시 원인 분석 없이 임의로 코드를 계속 수정하여 재실행하지 않습니다.
- **논리적 추론 및 보고**: 에러 발생 시 `원인 분석 -> 해결 방안 제안 -> 사용자 승인 대기` 절차를 준수합니다.

---

## 6. Git 커밋 및 거버넌스 (Governance & Git Standards)

- **거버넌스**: 본 지침은 프로젝트의 최상위 규범이며 헌법 개정 시 시맨틱 버저닝을 동반합니다.
- **커밋 메시지 규칙**: 헌법 및 프로젝트 컨벤션 형식(Conventional Commits)을 준수하고 "Why"에 집중하여 한국어로 작성합니다.
  - 예시: `docs: integrate constitution principles into master AGENTS.md v1.0.0`

---

**Version**: 1.0.0 | **Ratified**: 2026-07-24 | **Last Amended**: 2026-07-24
