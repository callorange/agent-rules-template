# CHANGELOG

본 문서는 `agents-template` 프로젝트의 규칙, 스킬, 서브에이전트 모듈 및 빌드 아티팩트의 주요 변경 사항과 개정 이력을 기록하는 문서입니다.
본 프로젝트는 [Keep a Changelog](https://keepachangelog.com/ko/1.0.0/) 및 [Semantic Versioning](https://semver.org/lang/ko/) 표준 규격을 준수합니다.

## [1.1.0] - 2026-08-01

### 🚀 Added
- **AI / LLM 애플리케이션 & RAG 아키텍처 규칙 모듈 (`rules/architecture/ai-llm-rag.md`)**:
  - 스키마 기반 타입 안전 구조화 출력 (Schema-driven Structured Outputs) 및 자가 치유 재시도 지침 수록
  - RAG 구조 보존 의미적 청킹(Semantic Chunking) 및 하이브리드 검색(BM25 + Dense Vector) 표준 정립
  - Model Context Protocol (MCP) 표준 인터페이스 및 프롬프트 주입(Prompt Injection) 방어 보안 수칙 수록
- **세션 맥락 인계 스킬 (`skills/handoff/`)**: 세션 리셋 및 컨텍스트 압축 시 작업 내역(`HANDOFF.md`)을 자동 정리/복구하는 공용 스킬 추가
- **외부 패키지 도입 vs 자체 구현 의사결정 룰 (`rules/architecture/library-package.md`)**:
  - 소스 복잡도/규모(100줄 이내 유틸 자체 구현) 및 프레임워크 내장 기능 기준의 의사결정 매트릭스(Decision Matrix) 신설
  - 유지보수 활성화, 커뮤니티 평판, 상용 라이선스, 전이적 의존성 4대 패키지 건전성 평가(Package Health Check) 명시
- **추천 외부 에이전트 스킬 가이드 ([README.md](README.md))**: 검증된 3rd-party 외부 스킬(`Leonxlnx/taste-skill` 등) 및 `npx skills add` 온디맨드 원클릭 설치 스크립트 안내 수록

### 🧹 Changed & Refactored
- **글로벌 에이전트 규격 v2.3 이식 및 코어 규칙 강화 (`rules/core/`, `dist/AGENTS.md`)**:
  - `01-base.md`: 지침 우선순위 4단계(상위 플랫폼 > 법적/보안 > 프로젝트 > 사용자 지시) 및 지침 충돌 시 작업 일시 중지(Fail-safe) 수칙 보강
  - `02-workflow.md`: 승인 없이 가능한 작업(Read-only)과 사전 승인 필수 작업(Side-effecting) 권한 분리 명시
  - `03-integrity.md`: 무단 생략 표기 금지 및 Surgical Update 유지하되 Linter/Formatter 등 기계적 변환 도구 사전 알림 후 수행 조항 반영
  - `04-standards.md`: 원인 가설 ➔ 검증 ➔ 해결책 설명의 3단계 디버깅 프로토콜(Structured Troubleshooting) 신설
- **비판적 검수 서브에이전트 명칭 단권화 (`subagents/auditor.md`, `.agents/agents/auditor.md`)**: 구형 `critical-evaluator` 명칭을 직관적이고 표준적인 감사관 서브에이전트(`auditor`)로 전면 개정 및 단권화
- **[AGENTS.md](file:///d:/Projects/Private/agent-rules-template/AGENTS.md) 구조 개정**: 행동 통제 수칙을 상단으로 전진 배치(Action-First Layout)하고 버전 `v1.1.0` 최신화
- **자율 검증 및 OS 호환성 정제 (`rules/core/02-workflow.md`)**: `tmux` 구문을 OS 종속성 없는 비동기 명령어 실행 도구(`manage_task` 등) 활용 규칙으로 정제하고 `git worktree` 격리 지침 추가
- **AI Attribution 제어 지침 범용화 (`rules/core/04-standards.md`)**: 특정 CLI 경로를 삭제하고 개발자 환경 설정 기반 커밋/PR 서명 노이즈 제거 지침으로 범용 추상화
- **웹 프론트엔드 자동화 검증 지침 추가 (`rules/architecture/web-frontend.md`)**: 브라우저 오토메이션 시 시각 좌표 대신 Accessibility Tree (Ref) 구조 타겟팅 지침 반영
- **Anti-Slop 프론트엔드 지침의 관심사 분리 (`rules/architecture/web-frontend.md`, `rules/styles/html-css.md`, `rules/frameworks/react.md`, `rules/frameworks/next.md`)**:
  - 기술 중립적 동적 뷰포트(`100dvh`), CSS Grid, 맥락별 라인길이 예외 지침(백오피스/대시보드 예외) 및 SVG 패스 직접 그리기 금지 반영
  - 단일 Accent Color 및 Color Lock 스타일 규칙 반영
  - 연속 이벤트 `useState` 남용 지양(React) 및 애니메이션 컴포넌트 말단 `'use client'` 격리 지침(Next.js) 반영
- **원자적 커밋 및 논리적 분할 수칙 수립 (`rules/core/04-standards.md`, `AGENTS.md`)**: 단일 트랜잭션(원본 수정, 문서화, `dist/` 빌드)은 정합성을 위해 1개 원자적 커밋으로 묶고, 목적이 무관한 별개 이슈 시에만 논리적으로 커밋을 분할하는 규격 반영
- **Python 코딩 및 패키징 수칙 정밀 강화 (`rules/styles/python.md`, `rules/packaging/package-python.md`)**:
  - McCabe 순환 복잡도 제한 (Ruff `C901`, `max-complexity = 10`) 규범 수술적 수록
  - 의존성 CVE 보안 취약점 감사 (`uv audit` / `pip-audit`) 및 Hypothesis 속성 기반 테스트(Property-based Testing) 수칙 반영
- **통합 파이썬 생태계 지식 베이스 스킬 추가 (`skills/python-ecosystem-kb/`)**: Awesome Python, Awesome Django, WikiDocs 14021 직링크 URL 연계 및 온디맨드 큐레이션 가이드 수록
- **Python & Django 생태계 레퍼런스 통합 (`rules/frameworks/django.md`, `rules/packaging/package-python.md`)**: `vinta/awesome-python`, `wsvincent/awesome-django`, `wikidocs.net/book/14021` 표준 생태계 레퍼런스 연계 및 실무 지침 보강
- **단계적 모호성 완전 해소 루프 수칙 수립 (`rules/core/02-workflow.md`, `AGENTS.md`)**: 요구사항 불명확 시 지레짐작 코딩을 금지하고 100% 명확화 후 구현에 진입하되, 합리적 기본값 제시 및 일괄 질문으로 대화 피로도를 차단하는 수칙 보강
- **`dist/AGENTS.md` 번들링 데드링크 자동 정제 파이프라인 보강 (`scripts/build_dist.py`)**: `01-base.md` 등 구형 로컬 상대 경로 링크를 정규표현식으로 정제하여 데드링크 완전 차단
- **파이썬 패키징 도구 유연성 보강 (`rules/packaging/package-python.md`)**: 기존 프로젝트의 `poetry`, `pip/venv`, `conda` 도구 호환성 및 존중 수칙 보강
- **외부 추천 에이전트 스킬 카탈로그 수립 (`rules/architecture/recommended-external-skills.md`)**: `taste-skill` (5개 세부 스킬) 및 `django-ai-plugins` (4개 세부 스킬)의 압축 테이블 카탈로그 모듈 신설 및 `dist/` 배포 편입
- **공용 배포 스킬 파이프라인 및 원본 동기화 (`skills/`, `scripts/build_dist.py`)**: `skills/` 원본 폴더 내 `.gitkeep` 삭제 및 `dist/skills/` 배포 원본 경로 동시 패키징 반영
- **모르는 지식 및 도구 탐색 실패 시 솔직한 시인 수칙 명시 (`rules/core/01-base.md`, `AGENTS.md`)**: 정보 불확실이나 도구 접근 실패(403 등) 시 지레짐작/거짓 답변(Hallucination)을 금지하고 솔직히 알 수 없음을 인정하는 헌법 수칙 보강
- **통합 파이썬 생태계 지식 베이스 스킬 신설 (`skills/python-ecosystem-kb/`)**: `Awesome Python`, `Awesome Django` 실시간 온디맨드 원격 수집 및 `WikiDocs 14021` 로컬 카탈로그 연계 패키지 추천 스킬 구축 및 `dist/` 배포 번들 편입

---

## [1.0.1] - 2026-07-26

### 🧹 Changed & Refactored
- **문서 동기화 (Doc-Code Disconnect 해소)**: [AGENTS.md](file:///d:/Projects/Private/agent-rules-template/AGENTS.md) 및 [README.md](file:///d:/Projects/Private/agent-rules-template/README.md) 상의 `rules/core/` 구조 표기를 실제 파일명(`01-base.md` ~ `05-docs-maintenance.md`)과 100% 동기화
- **헌법 V항 명확화**: [AGENTS.md](file:///d:/Projects/Private/agent-rules-template/AGENTS.md) 헌법 V항 구문을 실제 빌드 스크립트(`scripts/build_dist.py`) 및 무결성 검증 체계 호출 동작으로 명확히 현실화 및 정정

### 🗑️ Removed
- **형식적 테스트 폴더 삭제**: 유닛 테스트 코드가 없던 껍데기 디렉터리 `tests/` 및 캐시 완전 제거

---

## [1.0.0] - 2026-07-26

### 🚀 Added
- **프로젝트 헌법 및 AGENTS.md 표준 체계 정립**: 핵심 원칙 수립
- **규칙 원본 모듈 (`rules/`)**:
  - `core/`: 01-base, 02-workflow, 03-integrity, 04-standards, 05-docs-maintenance
  - `architecture/`: web-frontend, backend-api, database-orm, library-package, monorepo
  - `frameworks/`: django, react, next, vue, nuxt, fastapi, litestar
  - `packaging/`: package-npm, package-python, docker, deployment-nginx, deployment-python-server
  - `styles/`: python, typescript, javascript, html-css, go, cpp, csharp, dart
- **공용 스킬 모듈 (`skills/`)**: `gitignore-generator` 추가
- **공용 서브에이전트 모듈 (`subagents/`)**: `critical-evaluator.md` 추가
- **내부 전용 메타 모듈 (`.agents/`)**: `skills/rule-validator`, `agents/critical-evaluator.md` 배치
- **자동 조립 스크립트 (`scripts/build_dist.py`)**: `dist/` 배포 번들 자동 조립 도구 구축
- **문서화**: [AGENTS.md](file:///d:/Projects/Private/agent-rules-template/AGENTS.md) 및 [README.md](file:///d:/Projects/Private/agent-rules-template/README.md) 최신 프로젝트 구조 반영 및 [CHANGELOG.md](file:///d:/Projects/Private/agent-rules-template/CHANGELOG.md) 도입
