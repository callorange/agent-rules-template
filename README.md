# Shared AGENTS.md Standard & Generator

다양한 모바일/웹/백엔드 프로젝트에서 공용으로 사용할 수 있는 표준화된 `AGENTS.md` 지침 모듈을 정의하고, AI 에이전트(LLM)가 템플릿을 조합하여 최종 결과물(`dist/AGENTS.md`)을 직접 생성하도록 설계된 공용 표준 프로젝트입니다.

---

## 🎯 프로젝트 목적

AI 에이전트(Google Antigravity, Cursor, Claude Code, Windsurf 등)를 활용한 개발 과정에서 반복적으로 활용되는 기본 소통 규칙, 엄격한 실행 제어(Strict Execution Control), 기술 스택별 가이드라인을 모듈화하여 관리합니다.

외부 스크립트나 외부 도구 프레임워크에 의존하지 않고 **AI 에이전트(LLM)가 지침을 기반으로 직접 규칙을 읽어 `dist/` 디렉토리에 맞춤형 `AGENTS.md`를 조합/생성**합니다.

---

## 🏛️ 프로젝트 헌법 (Constitution)

본 프로젝트는 최상위 규범인 메인 지침 문서에 정의된 헌법 원칙에 따라 운영됩니다. 헌법의 상세 내용은 [AGENTS.md](file:///AGENTS.md)에서 확인할 수 있습니다.

### 핵심 5대 원칙
1. **범용성 및 표준화 (Universal Compatibility & Standardization)**: 특정 에이전트나 플랫폼에 종속되지 않는 표준 모듈 제공
2. **엄격한 실행 제어 (Strict Execution Control & Procedural Integrity)**: 에이전트의 안정적 운영을 위한 사전 승인 및 무단 수정 방지 절차 준수
3. **모듈화 및 확장성 (Modular Composition & Extensibility)**: Core, Workflow, Tech Stack별 독립 모듈화
4. **버전 관리 및 추적 가능성 (Semantic Versioning & Traceability)**: 시맨틱 버저닝(v1.0.0)을 통한 명확한 개정 이력 관리
5. **LLM 직접 생성 및 검증 (LLM-Driven Generation & Validation)**: 외부 스크립트 없이 AI 에이전트가 직접 모듈을 조합하여 `dist/`에 생성하고 검증

---

## 📂 프로젝트 구조

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

## 🚀 사용법 (AI 에이전트 직접 생성 방식)

### 1. AI 에이전트(LLM)에게 맞춤형 생성 요청
AI 에이전트에게 원하는 기술 스택과 조합 청사진(`blueprints/`)을 지정하여 `dist/` 폴더에 생성을 요청합니다:

> "현재 `blueprints/single-file.md.blueprint` 청사진을 참고하여 `rules/core/` 내 모듈과 `rules/stacks/web-frontend.md` 규칙을 조합해 `dist/AGENTS.md` 파일을 작성해라."

### 2. 생성 결과 확인 및 프로젝트 적용
AI 에이전트가 작성한 [dist/AGENTS.md](file:///dist/AGENTS.md) 파일 또는 모듈 구조를 대상 프로젝트의 루트 디렉토리로 적용하여 사용합니다.

---

## 📄 라이선스

본 프로젝트는 [MIT License](file:///LICENSE.md)에 따라 자유롭게 이용 및 수정, 재배포할 수 있습니다.
