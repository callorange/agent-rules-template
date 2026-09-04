# Shared AGENTS.md Standard & Generator

다양한 프로젝트에서 공용으로 사용할 규칙을 `agent_rules_template/bundle/` 단일 배포 번들로 조립·제공하는 에이전트 룰셋 표준 프로젝트입니다. 현재 버전은 **2.1.0**입니다.

---

## 🎯 프로젝트 목적

AI 에이전트(Google Antigravity, OpenAI Codex, Cursor, Claude Code, Windsurf 등)를 활용한 개발 과정에서 반복적으로 활용되는 기본 소통 규칙, 위험도 기반 실행 제어, 읽기/수정 권한 분리, 증거 기반 검증, 기술 스택별 실행 프로필 및 언어별 코딩 스타일 가이드를 모듈화하여 소스(`rules/`) 및 배포 아티팩트(`agent_rules_template/bundle/`)로 통합 관리합니다.

---

## 🏛️ 프로젝트 헌법 (Constitution)

본 프로젝트는 최상위 규범인 메인 지침 문서에 정의된 헌법 원칙에 따라 운영됩니다. 헌법의 상세 내용은 [AGENTS.md](file:///AGENTS.md)에서 확인할 수 있습니다.

### 핵심 원칙
1. **범용성 및 표준화 (Universal Compatibility & Standardization)**: 특정 에이전트나 플랫폼에 종속되지 않는 표준 모듈 제공 (OS/셸 및 도구 추상화)
2. **기획 중심·위험 비례 실행 (Planning-First, Risk-Proportional Execution)**: 복잡하거나 고위험인 작업에서는 목적·성공 기준·제약을 먼저 정렬하고, 가역적 로컬 작업에는 필요한 정보 확인과 최소 검증만 적용
3. **위험 기반 안전 경계 (Risk-Based Safety Boundaries)**: 외부·파괴적 변경만 사전 승인 대상으로 두고, 비신뢰 데이터를 지시와 분리
4. **정량적 검증 (Mechanical Validation)**: Linter, Type Checker, Test Runner, 빌드 스크립트로 결과를 검증하고 잔여 위험을 투명하게 보고
5. **자동 조립 및 추적 가능성 (Automated Assembly & Traceability)**: 조립·정적 검증으로 배포 번들을 최신화하고, 의미 있는 개정은 CHANGELOG에 기록

---

## 📂 프로젝트 구조

```text
agents-template/
├── rules/                   # 📌 SSOT: 규칙 원본 모듈 (단 1회만 정의되는 원본)
│   ├── core/                # 🎯 공용 핵심 규칙 모듈
│   │   ├── 01-base.md       # 진실의 계층, 컨텍스트·신뢰 경계, 증거 기반 검증, 보안
│   │   ├── 02-workflow.md   # 위험도 기반 실행 루프, 권한 분리, 검증·자가치유 경계
│   │   ├── 03-integrity.md  # 요청 범위 보호, 금지 표현, Surgical Edit, 기계적 변환
│   │   ├── 04-standards.md  # 3단계 디버깅 프로토콜, 코딩, 의미 있는 테스트, 커밋/CHANGELOG 표준
│   │   └── 05-docs-maintenance.md # 지속적 문서 관리 및 CHANGELOG 동기화
│   ├── architecture/        # 🏛️ 도메인 및 아키텍처 규칙 모듈
│   │   ├── web-frontend.md  # 웹 프론트엔드 특화 지침
│   │   ├── backend-api.md   # 백엔드 API 특화 지침
│   │   ├── database-orm.md  # 범용 DB 마이그레이션 & ORM 안전 지침
│   │   ├── library-package.md # 범용 라이브러리/모듈 공통 지침
│   │   ├── monorepo.md      # 모노레포 아키텍처 특화 지침
│   │   ├── ai-llm-rag.md    # AI / LLM 애플리케이션 & RAG 아키텍처 규칙
│   │   └── recommended-external-skills.md # 🚀 선택형 외부 에이전트 역량 카탈로그
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
│   │   ├── docker.md        # Docker 이미지를 직접 운영할 때의 컨테이너 지침
│   │   ├── deployment-nginx.md # Nginx를 운영할 때의 Reverse Proxy·보안 지침
│   │   └── deployment-python-server.md # Python 애플리케이션 서버를 직접 운영할 때의 지침
│   └── styles/              # 🎨 언어별 코딩 스타일 가이드 모듈
│       ├── python.md        # Python 코딩 스타일 지침 (Google Style Guide)
│       ├── typescript.md    # TypeScript 코딩 스타일 지침 (Google Style Guide)
│       ├── javascript.md    # JavaScript 코딩 스타일 지침 (Google Style Guide)
│       ├── html-css.md      # HTML/CSS 코딩 스타일 지침 (Google Style Guide)
│       ├── go.md            # Go 코딩 스타일 지침 (Effective Go)
│       ├── cpp.md           # C++ 코딩 스타일 지침 (Google Style Guide)
│       ├── csharp.md        # C# 코딩 스타일 지침 (Google Style Guide)
│       └── dart.md          # Dart/Flutter 코딩 스타일 지침 (Effective Dart)
├── guides/                  # 📚 비규범적 설계 참고 자료 (선택적으로 읽음)
│   ├── README.md            # guides/의 적용 경계와 사용 방법
│   └── prompt-context-engineering.md # 프롬프트·컨텍스트·Task Contract 설계 가이드
├── skills/                  # 🚀 배포용 공용 에이전트 스킬 원본 모듈 (SSOT)
│   ├── gitignore-generator/ # 언어/프레임워크별 .gitignore 최적화 자동 생성 스킬
│   ├── handoff/             # 장기 작업·세션 전환용 구조화 맥락 인계 스킬
│   └── python-ecosystem-kb/ # 검증된 Python·Django 후보군 우선 탐색 스킬
├── subagents/               # 🚀 배포용 공용 서브에이전트 원본 모듈 (SSOT)
│   └── auditor.md           # 코드 및 설계 변경사항 비판적 검수 및 감사 서브에이전트
├── .agents/                 # 🔒 이 프로젝트 전용 메타 스킬 및 서브에이전트 (배포 안 됨)
│   ├── skills/              # 메타 스킬 (rule-validator: 룰셋 무결성 정적 검증)
│   └── agents/              # 메타 서브에이전트 (auditor)
├── scripts/                 # 🛠️ 자동 조립 파이썬 스크립트
│   └── build_dist.py        # agent_rules_template/bundle/ 배포 아티팩트 자동 조립 도구
├── agent_rules_template/bundle/                    # 📦 배포용 아티팩트 디렉터리 (Git 트래킹 및 CI 배포)
│   ├── AGENTS.md            # 필수 핵심 규칙이 번들링된 통합 배포 파일
│   ├── rules/               # 온디맨드 기술 스택/스타일 규칙 모듈
│   ├── guides/              # 선택형 비규범적 설계 참고 자료
│   └── .agents/             # 🎯 Target 프로젝트 루트용 자동 호환 배포 디렉터리
│       ├── skills/          # agent_rules_template/bundle/.agents/skills/
│       └── agents/          # agent_rules_template/bundle/.agents/agents/
├── AGENTS.md                # 최상위 실행 지침 및 프로젝트 헌법 (Constitution)
├── README.md                # 프로젝트 안내 문서
├── CHANGELOG.md             # 프로젝트 개정 및 버전 이력 문서
└── LICENSE.md               # MIT 라이선스
```

---

## 🧩 모듈 적용 방식

- **Core**: 모든 대상 프로젝트에 적용하는 안전, 권한, 컨텍스트 수집, 검증의 공통 운영 헌장입니다. 작업은 관련 정보만 단계적으로 수집하고, 위험도에 맞는 최소 검증을 수행합니다.
- **Styles**: 수정·검토 대상 파일의 언어와 일치하는 모듈을 작업 전에 읽고 Core에 누적 적용합니다. 기존 프로젝트에서는 설정과 관례를 우선하며, 신규 프로젝트에서는 style 모듈을 기본 프로필로 사용합니다.
- **Frameworks / Architecture**: 사용하는 framework 규칙은 언어 style에 누적하고, architecture 규칙은 실제 작업의 책임과 기술이 일치할 때만 추가합니다. 관련 모듈이 여러 개면 하나만 고르지 않습니다.
- **언어 정책**: 커밋 메시지의 구조적 키워드(`feat`, `fix`, `docs`, `refactor` 등)는 영어 표준 형식을 사용하고, 설명과 본문은 명시된 프로젝트 언어를 우선합니다. 프로젝트 언어가 없으면 사용자의 주 언어를 따르며, Docstring과 주석은 기존 프로젝트의 언어 관례를 유지합니다.
- **Packaging**: Docker, Nginx, Python 애플리케이션 서버처럼 해당 기술을 직접 운영할 때만 적용합니다. PaaS, 서버리스, 관리형 ingress 등은 플랫폼의 공식 운영 가이드를 우선합니다.
- **Skills / Subagents**: 특정 전문성, 장기 인계, 독립 감사가 필요한 경우에만 선택적으로 사용합니다. 설치나 서브에이전트 호출은 기본 동작이 아닙니다.
- **Guides**: 규칙·프롬프트·Task Contract·agent harness를 설계하거나 검토할 때만 선택적으로 읽는 비규범적 참고 자료입니다. 일반 코드 작업에 자동 적용하지 않으며, 소비 프로젝트의 자체 설계 가이드 또는 정책이 있으면 그것을 우선합니다.

---

## 🗺️ 소비 프로젝트용 규칙 활성화 템플릿

소비 프로젝트는 실제 경로와 기술 스택을 아래 표의 `<...>` 자리에 채워 자체 `AGENTS.md`에 기록합니다. 표의 경로 예시는 설명용이며 특정 디렉터리 구조를 강제하지 않습니다.

| 작업 대상 또는 경로 | 누적 적용할 규칙 | 프로젝트에서 확정할 조건 |
| :--- | :--- | :--- |
| Python 파일 (`<python-paths>`) | Core + `styles/python.md` + 해당 framework | framework 사용 여부와 public 범위 |
| Django 코드 (`<django-paths>`) | 위 규칙 + `frameworks/django.md` + 필요 시 `architecture/backend-api.md`, `architecture/database-orm.md` | API·ORM·migration을 실제로 다루는지 |
| TypeScript 파일 (`<typescript-paths>`) | Core + `styles/typescript.md` + 해당 시 React, Next 또는 Vue 규칙 | 파일별 framework 및 렌더링 환경 |
| DB schema·migration (`<migration-paths>`) | 해당 언어 style + framework + `architecture/database-orm.md` | 사용하는 DB와 migration 도구 |
| Packaging 설정 (`<package-paths>`) | 해당 언어 style + `packaging/package-<ecosystem>.md` | 배포 패키지를 실제로 생성하는지 |
| 배포 설정 (`<deployment-paths>`) | 해당 언어 style + 실제 기술의 `packaging/deployment-*.md` 또는 `packaging/docker.md` | 직접 운영하는 배포 기술과 관리형 플랫폼 경계 |

### 소비 프로젝트 설정 체크리스트

- [ ] 사용 언어별 필수 style 규칙과 framework별 활성화 조건
- [ ] architecture 및 packaging 규칙을 추가하는 경로·작업·기술 조건
- [ ] 문서화 언어와 public API·public 코드 요소의 범위
- [ ] framework override, lifecycle hook, callback의 문서화 예외
- [ ] 언어별 docstring 또는 documentation comment 형식과 기존 프로젝트 우선 관례
- [ ] formatter, linter, type checker 연결 및 CI에서 강제할 문서화 규칙
- [ ] test, migration, generated file의 적용 또는 제외 범위
- [ ] 자동 검사 항목과 의미 검토가 필요한 code review 항목
- [ ] 처리 목적·domain 단계·불변조건 전환에서 문맥 주석이 필요한 기준
- [ ] 긴 처리 흐름에서 구획 주석과 함수·객체 분리를 선택하는 기준
- [ ] 규칙 변경 후 실행할 build, test 및 정적 검증 명령

---

## 📊 하네스 경량화 효과 측정

실행 하네스 변경은 대표 작업을 기준으로 전후를 비교해 판단합니다. 기본 지침 토큰량, 추가 질문 횟수, 완료 시간, 검증 실패, 재작업률을 기록하고, 안전·정확성을 낮추지 않는 범위에서만 추가 축소 또는 통폐합을 결정합니다.

---

## 🚀 사용법 (Usage)

### 1. 로컬 번들 조립 스크립트 실행 (`scripts/build_dist.py`)
규칙(`rules/`), 가이드(`guides/`), 스킬(`skills/`), 서브에이전트(`subagents/`) 모듈을 추가/수정한 후, 아래 명령어를 실행하면 `agent_rules_template/bundle/` 배포 아티팩트가 자동 생성됩니다:

```bash
python3 scripts/build_dist.py
```

### 2. 규칙 무결성 정적 검증 스크립트 실행 (`rule-validator`)
모듈 수정 또는 조립 후 금지 표현, UTF-8 인코딩, 상대 링크 유효성 및 `agent_rules_template/bundle/` 최신 동기화 상태를 검증합니다:

```bash
python3 .agents/skills/rule-validator/scripts/validate_rules.py
```

*(참고: AI 에이전트와 함께 작업 시, 에이전트가 rules 수정 직후 이 스크립트들을 자동 실행하여 agent_rules_template/bundle/와 무결성을 유지합니다.)*

### 3. 배포 및 소비 프로젝트 동기화

```text
SSOT → build_dist.py → agent_rules_template/bundle/ → uvx / agent-rules → Consumer Project
```

`build_dist.py`는 source를 검증 가능한 `agent_rules_template/bundle/` 계약으로 조립하고, sync tool은 source layout을 해석하지 않고 bundle metadata만으로 소비 프로젝트를 갱신합니다. 신규 설치·업데이트에는 다음 중 하나를 사용합니다.

```bash
agent-rules
uvx --from git+https://github.com/callorange/agent-rules-template.git agent-rules
```

기존 `AGENTS.md`에 marker가 없으면 기존 내용은 `# Project Rules` 아래에 보존됩니다. Template은 marker 사이의 Managed Block과 metadata에 등록된 파일만 소유하며, `Project Rules` 및 프로젝트가 만든 파일은 보존합니다. Managed 파일은 직접 수정하거나 formatter의 자동 변경 대상으로 두지 마십시오. 프로젝트별 예외는 Project Rules 또는 프로젝트 소유 rule 파일에 작성합니다.

`agent_rules_template/bundle/metadata.json`은 새 canonical target, 소비 프로젝트의 `.agent-rules-template.json`은 마지막 정상 설치 baseline입니다. sync는 Actual Local과 baseline hash를 비교해 로컬 변경을 먼저 감지합니다. 텍스트 hash는 BOM, 줄바꿈, NFC/NFD, 마지막 newline 차이를 무시합니다.

```bash
# Template-managed 로컬 변경만 현재 bundle로 복원
agent-rules --force

# AGENTS.md의 Project Rules까지 새 구조로 교체 (관리 파일 변경은 여전히 보호)
agent-rules --replace

# 두 의도를 명시적으로 함께 적용
agent-rules --replace --force
```

Migration은 기계적 작업일 뿐 기존 Project Rules와 Template 규칙의 의미 중복을 제거하지 않습니다. Local metadata 도입 전 복사한 파일은 bundle의 canonical file record와 완전히 같을 때만 자동 adoption하며, 하나라도 다르면 Project-owned conflict로 중단합니다. 필요하면 LLM에게 Project Rules를 검토해 프로젝트 고유 규칙만 남기도록 요청하십시오.

Local metadata가 손상되거나 기존 managed 설치에서 누락되면 sync는 중단합니다. `--force`도 baseline 손상이나 Project-owned 파일 충돌을 무시하지 않습니다. `--replace`는 손상된 AGENTS marker를 재생성하지만 다른 managed 파일 변경까지 무시하지 않습니다.

Bundle 파일명은 NFC여야 하며 NFD source/bundle 경로는 build가 거부합니다. 소비 프로젝트에서는 NFC logical key로 유일한 실제 경로를 찾아 NFD 파일명도 보존합니다. 같은 key에 여러 경로가 대응되면 모든 옵션에서 중단합니다. 쓰기·삭제 대상의 symlink 및 경로 우회도 거부합니다.

적용 전 파일을 staging하고, 적용 중 예외가 발생하면 변경한 파일을 복구합니다. Local metadata는 결과 검증 후 마지막으로 교체합니다. 프로세스 강제 종료·전원 장애나 동시 외부 파일 변경까지 원자적으로 처리하는 transaction은 아니므로 sync 중에는 대상 파일을 동시에 수정하지 마십시오.

---

## 🚀 선택형 외부 에이전트 역량 (Optional Agent Capabilities)

본 룰셋 템플릿과 함께 검토할 수 있는 3rd-party 외부 에이전트 스킬 후보군입니다. 자동 설치 또는 필수 의존성이 아니며, 현재 기본 도구·규칙으로 충분한지 먼저 판단하십시오. 설치 전에는 원본 README에서 최신 옵션을 확인하고 유지보수 상태, 라이선스, 권한 및 전이 의존성을 검토합니다. 상세 하위 스킬 옵션과 적용 조건은 [recommended-external-skills.md](rules/architecture/recommended-external-skills.md)에서 확인할 수 있습니다:

- **[taste-skill](https://github.com/Leonxlnx/taste-skill)**: Anti-Slop 디자인 규격, CSS Grid 및 모던 프론트엔드 디자인 스킬
- **[django-ai-plugins](https://github.com/vintasoftware/django-ai-plugins)**: Django ORM, DRF, Celery 비동기, 안전한 DB 마이그레이션 및 코드 리뷰어 지침 스킬

---

## 📄 라이선스

본 프로젝트는 [MIT License](file:///LICENSE.md)에 따라 자유롭게 이용 및 수정, 재배포할 수 있습니다.
