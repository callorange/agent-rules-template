# Django Architecture & Development Rules (Django 특화 개발 규칙)

Django 및 Django REST Framework (DRF) / Django Ninja 기반 프로젝트에 적용되는 아키텍처 및 코딩 규칙입니다.

---

## 🏛️ 1. 프로젝트 구조 및 도메인 분리 (Project Structure)

- **도메인 단위 앱 분리 (Modular Apps)**: 
  단일 앱에 모든 모델과 뷰를 몰아넣지 말고, 비즈니스 도메인 단위(`users`, `orders`, `payments` 등)로 앱을 명확히 분리하십시오.
- **Service & Selector 패턴 (Fat Model 방지)**:
  - 비즈니스 로직이 복잡해질 경우 Model이나 View에 직접 작성하지 말고 `services.py`(CUD 비즈니스 로직) 및 `selectors.py`(조회 로직)로 분리하십시오.
  - **Model**: 데이터 구조, 데이터 검증 및 기본 속성 메서드만 유지하십시오.
  - **View / API**: 요청 수신, 입력 검증 호출, 서비스 레이어 호출 및 응답 반환 역할만 수행하십시오.

---

## 🗄️ 2. ORM 및 쿼리 최적화 (ORM & DB Performance)

- **N+1 쿼리 방지 필수**:
  - 1:1 및 N:1 관계 조회 시에는 `select_related()`를 사용하십시오.
  - 1:N 및 M:N 관계 조회 시에는 `prefetch_related()`를 필수 적용하십시오.
- **대량 데이터 처리**:
  - 다수의 객체 생성/수정 시 반복문 내부 `save()` 호출을 금지하고 `bulk_create()` 및 `bulk_update()`를 사용하십시오.
- **트랜잭션 세분화**:
  - 복수의 DB CUD 작업이 수반되는 비즈니스 로직에는 `@transaction.atomic`을 명시하여 데이터 일관성을 보장하십시오.
- **`only()` 및 `defer()` 활용**: 대용량 텍스트나 불필요한 컬럼 조회를 피하기 위해 필요한 필드만 선택 조회하십시오.

---

## 🔒 3. API 및 입력 검증 (DRF / Ninja Standards)

- **Serializer / Schema 검증**:
  - 클라이언트 입력값 검증은 반드시 Serializer (DRF) 또는 Pydantic Schema (Django Ninja)를 거치도록 하십시오.
- **통일된 API 응답 및 에러 규격**:
  - 커스텀 예외 핸들러(`custom_exception_handler`)를 등록하여 예외 발생 시 통일된 JSON 에러 구조(`{ "success": false, "error": { "code": "...", "message": "..." } }`)를 반환하십시오.
- **Pagination 필수**: 목록 조회 API는 서버 과부하 방지를 위해 반드시 페이징(`PageNumberPagination` 또는 `CursorPagination`)을 적용하십시오.

---

## 🔐 4. 보안 및 환경 설정 (Security & Config)

- **설정 분리 (`settings.py`)**:
  - Secret Key, DB Password, API Key 등 자격 증명은 절대 하드코딩하지 말고 환경 변수(`django-environ` 또는 `pydantic-settings`)로 관리하십시오.
  - 개발(`local.py`), 테스트(`test.py`), 운영(`prod.py`) 설정을 분리하여 관리하십시오.
- **배포 보안 옵션**:
  - 운영 환경에서는 `DEBUG = False`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `SECURE_SSL_REDIRECT` 등의 보안 옵션을 철저히 확인하십시오.

---

## ⚙️ 5. 비동기 작업 및 마이그레이션 (Celery & Migrations)

- **비동기 태스크 분리**:
  - 이메일 발송, 외부 API 연동, 대용량 파일 처리 등 요청-응답 주기를 지연시키는 작업은 Celery / Redis 등의 백그라운드 태스크로 분리하십시오.
- **마이그레이션 이력 관리**:
  - 마이그레이션 파일(`makemigrations`)은 항상 테스트 후 Git 버전 관리에 포함시키고, 배포 시 `migrate`를 안전하게 수행하십시오.
