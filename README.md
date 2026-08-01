# Shared AGENTS.md Standard & Generator

다양한 모바일/웹/백엔드 프로젝트에서 공용으로 사용할 수 있는 표준화된 `AGENTS.md` 지침 모듈을 정의하고, 모듈화된 규칙(`rules/`)을 최적화된 배포 번들(`dist/AGENTS.md`)로 조립하여 제공하는 공용 에이전트 룰셋 표준 프로젝트입니다.

---

## 🎯 프로젝트 목적

AI 에이전트(Google Antigravity, OpenAI Codex, Cursor, Claude Code, Windsurf 등)를 활용한 개발 과정에서 반복적으로 활용되는 기본 소통 규칙, 엄격한 실행 제어(Strict Execution Control), 읽기/수정 권한 분리, 3단계 디버깅 프로토콜, 기술 스택별 가이드라인 및 언어별 코딩 스타일 가이드를 모듈화하여 소스(`rules/`) 및 배포 아티팩트(`dist/`)로 통합 관리합니다.

---

## 🏛️ 프로젝트 헌법 (Constitution)

본 프로젝트는 최상위 규범인 메인 지침 문서에 정의된 헌법 원칙에 따라 운영됩니다. 헌법의 상세 내용은 [AGENTS.md](file:///AGENTS.md)에서 확인할 수 있습니다.

### 핵심 5대 원칙
1. **범용성 및 표준화 (Universal Compatibility & Standardization)**: 특정 에이전트나 플랫폼에 종속되지 않는 표준 모듈 제공 (OS/셸 및 도구 추상화)
2. **엄격한 실행 제어 (Strict Execution Control & Procedural Integrity)**: 에이전트의 안정적 운영을 위해 승인 없는 작업(Read-only/격리 테스트)과 사전 승인 필요 작업(Side-effecting)을 구분하고 절차 준수
3. **모듈화 및 확장성 (Modular Composition & Extensibility)**: Core, Architecture, Frameworks, Packaging, Styles별 독립 모듈화
4. **버전 관리 및 추적 가능성 (Semantic Versioning & Traceability)**: 명확한 개정 이력 및 릴리즈 관리
5. **자동 조립 및 검증 (Automated Assembly & Validation)**: 조립 스크립트(`scripts/build_dist.py`) 및 무결성 정적 검증 스크립트(`validate_rules.py`)를 통해 `dist/` 배포 번들을 100% 무결하게 유지

---

## 📂 프로젝트 구조

```text
agents-template/
├── rules/                   # 📌 SSOT: 규칙 원본 모듈 (단 1회만 정의되는 원본)
│   ├── core/                # 🎯 공용 핵심 규칙 모듈
│   │   ├── 01-base.md       # 진실의 계층, 기계적 하네스, 보안, 정직성, 충돌 수칙
│   │   ├── 02-workflow.md   # 행동 프로토콜, 권한 분리(Read-only vs Side-effecting), 자가치유
│   │   ├── 03-integrity.md  # 출력 무결성 원칙, 금지 표현, Surgical Edit, 포매터 알림
│   │   ├── 04-standards.md  # 3단계 디버깅 프로토콜, 코딩, 의미 있는 테스트, 커밋/CHANGELOG 표준
│   │   └── 05-docs-maintenance.md # 지속적 문서 관리 및 CHANGELOG 동기화
│   ├── architecture/        # 🏛️ 도메인 및 아키텍처 규칙 모듈
│   │   ├── web-frontend.md  # 웹 프론트엔드 특화 지침
│   │   ├── backend-api.md   # 백엔드 API 특화 지침
│   │   ├── database-orm.md  # 범용 DB 마이그레이션 & ORM 안전 지침
│   │   ├── library-package.md # 범용 라이브러리/모듈 공통 지침
│   │   ├── monorepo.md      # 모노레포 아키텍처 특화 지침
│   │   ├── ai-llm-rag.md    # AI / LLM 애플리케이션 & RAG 아키텍처 규칙
│   │   └── recommended-external-skills.md # 🚀 외부 추천 에이전트 스킬 카탈로그
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
│   ├── handoff/             # 세션 맥락 인계 및 HANDOFF.md 자동 생성 스킬
│   └── python-ecosystem-kb/ # 파이썬 및 Django 생태계 지식 베이스 스킬
├── subagents/               # 🚀 배포용 공용 서브에이전트 원본 모듈 (SSOT)
│   └── auditor.md           # 코드 및 설계 변경사항 비판적 검수 및 감사 서브에이전트
├── .agents/                 # 🔒 이 프로젝트 전용 메타 스킬 및 서브에이전트 (배포 안 됨)
│   ├── skills/              # 메타 스킬 (rule-validator: 룰셋 무결성 정적 검증)
│   └── agents/              # 메타 서브에이전트 (auditor)
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

## 🚀 사용법 (Usage)

### 1. 로컬 번들 조립 스크립트 실행 (`scripts/build_dist.py`)
규칙(`rules/`), 스킬(`skills/`), 서브에이전트(`subagents/`) 모듈을 추가/수정한 후, 아래 명령어를 실행하면 `dist/` 배포 아티팩트가 0.01초 만에 자동 생성됩니다:

```bash
python3 scripts/build_dist.py
```

### 2. 규칙 무결성 정적 검증 스크립트 실행 (`rule-validator`)
모듈 수정 또는 조립 후 금지 표현, UTF-8 인코딩, 상대 링크 유효성 및 `dist/` 최신 동기화 상태를 검증합니다:

```bash
python3 .agents/skills/rule-validator/scripts/validate_rules.py
```

*(참고: AI 에이전트와 함께 작업 시, 에이전트가 rules 수정 직후 이 스크립트들을 자동 실행하여 dist/와 무결성을 유지합니다.)*

### 3. GitHub Release 배포 아티팩트 활용 (타 프로젝트 적용)
GitHub Release 페이지의 **`Latest Continuous Release`**에서 **`agents-template-dist.zip`**을 다운로드하여 대상 프로젝트 루트 디렉터리에 해제하면 즉시 최신 에이전트 실행 환경이 세팅됩니다.

---

## 🚀 추천 외부 에이전트 스킬 (Curated External Agent Skills)

본 룰셋 템플릿과 함께 조합하여 사용할 수 있는 검증된 3rd-party 외부 에이전트 스킬 목록입니다. 상세 하위 스킬 옵션과 제안 가이드는 [recommended-external-skills.md](rules/architecture/recommended-external-skills.md) 카탈로그 모듈에 정리되어 있습니다:

- **[python-ecosystem-kb](skills/python-ecosystem-kb/)**: 파이썬 및 Django 생태계 라이브러리(Awesome Python, Awesome Django, WikiDocs 14021) 온디맨드 실시간 큐레이션 및 패키지 추천 내장 스킬
- **[taste-skill](https://github.com/Leonxlnx/taste-skill)**: Anti-Slop 디자인 규격, CSS Grid 및 모던 프론트엔드 디자인 스킬
- **[django-ai-plugins](https://github.com/vintasoftware/django-ai-plugins)**: Django ORM, DRF, Celery 비동기, 안전한 DB 마이그레이션 및 코드 리뷰어 지침 스킬
- **언어/프레임워크 생태계 레퍼런스**: 파이썬 및 Django 개발 시 [Awesome Python](https://github.com/vinta/awesome-python), [Awesome Django](https://github.com/wsvincent/awesome-django), [위키독스 지식 베이스](https://wikidocs.net/book/14021)가 각 룰셋 모듈([package-python.md](rules/packaging/package-python.md), [django.md](rules/frameworks/django.md)) 및 전용 온디맨드 스킬로 연계되어 있습니다.

---

## 📄 라이선스

본 프로젝트는 [MIT License](file:///LICENSE.md)에 따라 자유롭게 이용 및 수정, 재배포할 수 있습니다.
