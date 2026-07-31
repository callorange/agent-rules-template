# Coding & Commit Standards (코딩 및 커밋 표준)

새로운 코드를 작성하거나 리팩토링 및 커밋 작업 수행 시 적용되는 표준 지침입니다. **일관성(Consistency)은 가이드라인보다 우선합니다.** 기존 파일의 스타일을 최대한 유지하십시오.

---

## 📏 1. 기계적 린팅 위임 및 최소 변경 원칙

- **린팅 위임**: 탭 사이즈, 세미콜론 유무, 따옴표 종류 등 단순 포맷팅은 AI가 주관적으로 결정하지 않고, 프로젝트에 설정된 포맷터(Prettier, ruff, `gofmt` 등)를 실행하여 기계적으로 스타일을 맞추십시오.
- **최소 변경 원칙 (No Vanity Edits)**: 요청받은 작업과 직접적인 관련이 없는 주변 코드(동작에 영향을 주지 않는 단순 스타일 수정, 무관한 주석 변경)는 **[절대]** 임의로 수정하지 마십시오.

---

## 🧪 2. 의미 있는 테스트 및 Mocking 방지 (Meaningful Testing)

- **가짜 테스트 금지**: Assertion(검증문)이 없거나 무조건 `true`를 반환하여 빌드만 통과시키는 형식적인 테스트 코드를 절대 작성하지 마십시오.
- **과도한 Mocking 지양**: 실제 비즈니스 로직 및 런타임 오류까지 감춰버리는 무분별한 Mocking을 피하십시오. 외부 네트워크/입출력만 Mocking하고, 내부 로직 및 데이터 변환은 실제 객체와 상태를 검증하십시오.

---

## 📝 3. Why 중심 주석 (Contextual Comments)

- 주석은 코드가 '무엇(What)'을 하는지 번역하지 마십시오. 코드는 스스로를 설명해야 합니다.
- 주석은 **[반드시]** '왜(Why)' 이런 비직관적인 로직을 선택했는지, 어떤 엣지 케이스를 방어하기 위함인지를 설명할 때만 작성하십시오.

---

## 📌 4. 커밋 메시지 규약 (Commit Conventions)

- 커밋 메시지는 Conventional Commits 규약(`feat:`, `fix:`, `docs:`, `refactor:` 등)을 준수하여 작성하십시오.
- 프로젝트 내 특정 언어 규칙(예: 한글 작성 등)이 있다면 이를 최우선으로 따르십시오.
  - 예시: `docs: update core standards and formatting rules`
- **자동 기여 문구 (Attribution) 제어**: AI 도구(Claude Code 등)가 커밋/PR 생성 시 자동으로 삽입하는 `Co-Authored-By` 트레일러나 푸터 링크를 제어하려는 경우, 개발자 글로벌 설정(`~/.claude/settings.json` 내 `"attribution": { "commit": "", "pr": "", "sessionUrl": false }`)을 통해 구성하도록 권장합니다.

---

## 📋 5. CHANGELOG 작성 및 관리 규약 (Keep a Changelog)

- **적용 조건 및 작성 시점**: 프로젝트 루트에 `CHANGELOG.md`가 존재하거나 버전 릴리즈/태그 작업 지시가 있을 때 적용하십시오. 단발성 기능 구현 시에는 `## [Unreleased]` 섹션에 추가하고, 릴리즈 시점에 버전과 날짜(예: `## [1.0.0] - 2026-07-26`)로 변환하십시오.
- **Keep a Changelog & SemVer 준수**: 버전 변경 이력은 [Keep a Changelog](https://keepachangelog.com/ko/1.0.0/) 및 시맨틱 버저닝 규격을 엄격히 준수하십시오.
- **표준 카테고리 매핑**: 변경 사항은 커밋 타입에 대응하는 표준 카테고리 아래에 작성하십시오:
  - `Added`: 새로운 기능 추가 (`feat:`)
  - `Changed`: 기존 기능의 변경 또는 개선 (`refactor:`, `style:`, `perf:`)
  - `Deprecated`: 향후 삭제될 예정인 기능
  - `Removed`: 삭제된 기능
  - `Fixed`: 버그 수정 (`fix:`)
  - `Security`: 보안 취약점 개선
- **Why 중심의 유저 친화적 서술**: 단순 Git 커밋 메시지 목록을 복사하지 말고, 사용자 및 개발자 관점에서 변경 이유(Why)와 유용한 가치를 명확한 마크다운 불릿 항목으로 작성하십시오.
