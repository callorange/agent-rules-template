# Continuous Documentation Maintenance (지속적 문서 유지보수 규칙)

본 지침은 다양한 프로젝트 환경에서 코드베이스의 변경 사항이 핵심 문서(README, AGENTS.md, constitution.md 등)에 지속적으로 반영되도록 동기화하는 규칙입니다.

---

## 🔄 1. 역할 기반 문서 추상화 (Role-Based Document Abstraction)

프로젝트마다 문서 파일명과 구조가 상이하므로, 특정 파일명이 아닌 **문서의 역할(Doc Role)** 을 기준으로 업데이트 대상을 식별합니다:

1. **진입점 문서 (Entrypoint Doc)**: 프로젝트 소개, 설치/실행 방법, 주요 CLI 및 설정 정보 (`README.md`, `INDEX.md` 등)
2. **거버넌스 문서 (Governance Doc)**: AI 실행 지침, 코드 가이드, 개발 헌법 및 실행 프로토콜 (`AGENTS.md`, `constitution.md`, `.cursorrules`, `CLAUDE.md` 등)
3. **아키텍처/스펙 문서 (Architecture Doc)**: 모듈 구조, 시스템 설계, API 명세 및 도메인 지식 (`docs/architecture.md`, SpecKit `spec.md` 등)
4. **변경 이력 문서 (History Doc)**: 사용자 및 개발자 관점의 버전별 변경 이력 (`CHANGELOG.md`, `HISTORY.md` 등)

---

## 🔍 2. 동적 문서 탐색 및 매핑 프로토콜 (Dynamic Discovery & Mapping Protocol)

1. **동적 탐색 (Dynamic Discovery)**:
   - AI 에이전트는 코드 변경 후 작업 마무리 단계에서 프로젝트 루트 및 `docs/` 디렉터리의 실제 존재하는 문서 파일들을 조회합니다.
2. **프로젝트 설정 명세 최우선 적용 (Configuration First)**:
   - 만약 프로젝트 설정 문서(예: `AGENTS.md`) 내에 별도의 `Documentation Mapping` 명세가 기술되어 있는 경우, 해당 매핑 정보를 최우선하여 적용합니다.
3. **존재하지 않는 파일 무단 생성 금지**:
   - 프로젝트에 기존 존재하지 않는 문서(예: `CHANGELOG.md`나 `constitution.md`)를 사용자의 명시적 지시 없이 임의로 신규 작성하지 않습니다.

---

## 🎯 3. 문서 역할별 갱신 트리거 (Update Triggers)

- **진입점 문서 갱신 트리거**:
  - 의존성 패키지 추가/삭제, 빌드 및 실행 스크립트(`package.json`, `pyproject.toml` 등) 변경 시
  - 환경 변수(`.env`) 또는 CLI 사용법 변경 시
- **거버넌스 문서 갱신 트리거**:
  - 프로젝트 디렉터리/모듈 구조 변경 시 (프로젝트 구조 트리 갱신)
  - 개발 스타일 가이드, AI 스킬/서브에이전트 추가 및 제거 시
- **아키텍처/스펙 문서 갱신 트리거**:
  - 핵심 데이터 구조, DB 스키마, 주요 모듈 간 의존성 파이프라인 개정 시
- **변경 이력 문서 갱신 트리거**:
  - 사용자 관점의 새로운 기능 추가(feat), 주요 버그 수정(fix), 하위 호환성 파괴 변경 시

---

## ✅ 4. 검증 및 수정 절차 (Verification & Execution)

1. **영향도 평가**: 작업 완료 전, 이번 코드 변경으로 인해 유효하지 않게 된 문서 구문이 있는지 확인합니다.
2. **수술적 부분 편집 (Surgical Edit)**: 문서 전체를 새로 쓰지 않고, 변경이 필요한 절 및 불릿 항목만 정밀하게 업데이트합니다.
3. **무단 생략 절대 금지**: `rules/core/03-integrity.md` 지침에 따라 문서 수정 시 임의의 줄임표(`...`)나 생략 구문을 남기지 않습니다.
