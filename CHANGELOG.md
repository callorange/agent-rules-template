# CHANGELOG

본 문서는 `agents-template` 프로젝트의 규칙, 스킬, 서브에이전트 모듈 및 빌드 아티팩트의 주요 변경 사항과 개정 이력을 기록하는 문서입니다.
본 프로젝트는 [Keep a Changelog](https://keepachangelog.com/ko/1.0.0/) 및 [Semantic Versioning](https://semver.org/lang/ko/) 표준 규격을 준수합니다.

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
