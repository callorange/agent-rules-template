# General Library & Module Rules (범용 라이브러리 및 패키지 아키텍처 규칙)

언어와 생태계에 국한되지 않고 모든 공용 라이브러리, 모듈, SDK 개발 프로젝트에 공통으로 적용되는 기본 설계 및 품질 관리 규칙입니다.

---

## 📦 1. 인터페이스 설계 및 하위 호환성 (API Design & SemVer)

- **명확한 Public API 분리**: 외부에 노출되는 공용 모듈(Public Interface)과 내부 구현 모듈(Internal Implementation)을 엄격히 구분하고, 명시적인 인터페이스를 통해서만 노출하십시오.
- **Breaking Change 최소화**: 메서드 시그니처 수정이나 반환 타입 변경 시 기존 사용자에게 영향을 주지 않도록 Deprecation 경고 기간을 두고 시맨틱 버저닝(MAJOR.MINOR.PATCH) 규칙을 준수하십시오.
- **Side-Effects 최소화**: 모듈 임포트 시 글로벌 상태를 직접 변경하거나 예기치 않은 부작용(Side Effect)이 발생하지 않도록 순수 함수(Pure Functions) 중심 설계를 지향하십시오.

---

## 🧪 2. 테스트 격리 및 문서화 (Testing & Documentation)

- **독립적 유닛 테스트**: 모든 Public API에 대해서는 외부 환경 의존성 없이 100% 독립적으로 실행 가능한 단위 테스트(Unit Tests)를 작성하십시오.
- **인터페이스 문서화**: 외부에 공개되는 모든 클래스, 함수, 매개변수에는 명확한 용도와 예시를 포함하는 공식 문서 주석(Docstring / Type Comments)을 작성하십시오.

---

## 🚀 3. 의존성 관리 및 독립성 (Dependencies & Packaging)

- **최소 의존성 원칙 (Minimal Dependencies)**: 무거운 외부 라이브러리 추가를 최소화하여 설치 용량과 보안 취약점 노출을 줄이십시오.
- **명확한 의존성 분리**: 런타임 의존성(Dependencies)과 개발/테스트 전용 의존성(Dev Dependencies)을 엄격히 구분하십시오.
- **독립 설치 스펙 준수**: 라이브러리가 타 시스템이나 프로젝트에 모듈로 통합될 때 예기치 않은 전역 상태 오염이나 내부 경로 결합이 발생하지 않도록 캡슐화하십시오.
