# Python Packaging Rules (Python & PyPI 생태계 패키징 규칙)

Python 생태계(PyPI, uv, Poetry, Hatch, Setuptools 등)의 라이브러리 및 패키지 개발/배포에 적용되는 패키징 규칙입니다.

---

## 🐍 1. 현대적 패키징 표준 (PEP 621 pyproject.toml)

- **pyproject.toml 표준 명세**: Legacy `setup.py` 대신 PEP 621 규격을 준수하는 `pyproject.toml`을 단일 메타데이터 매니페스트로 사용하십시오.
- **선언적 의존성 통제**: 모든 파이썬 의존성은 `pyproject.toml` 및 프로젝트 선언 Lockfile(`uv.lock`, `poetry.lock` 등)에 선언적으로 명세/잠금 관리되어야 하며, 임의의 ad-hoc `pip install`은 금지됩니다. 환경 동기화 시에는 프로젝트에 지정된 패키지 매니저의 동기화 명령어(예: `uv sync`, `poetry install`)를 사용하십시오.
- **의존성 그룹 분류 표준 (Dependency Grouping)**:
  - **프로덕션 런타임 의존성 (`[project.dependencies]`)**: 서비스 구동 및 SDK 실행 시 필수적인 런타임 패키지만 선언합니다.
  - **개발/테스트 전용 의존성 (`[dependency-groups.dev]` / `[tool.poetry.group.dev.dependencies]`)**: pytest, ruff, mypy 등 개발 전용 도구는 프로덕션 이미지 및 배포 패키지 경량화를 위해 반드시 dev 그룹으로 격리 선언하십시오.
- **빌드 백엔드 명시**: `[build-system]` 섹션에 빌드 툴(hatchling, flit_core, poetry-core, setuptools 등)을 명확히 정의하십시오.
- **의존성 범위 지정**: `dependencies` 필드에 과도하게 고정된 버전(`==`) 대신 최소/호환 가능한 범위 지정자(`>=`, `~=`)를 사용하십시오.

---

## 🏷️ 2. Public API 캡슐화 및 타입 지원 (PEP 561)

- **`__all__`을 통한 공개 제어**: 패키지 `__init__.py` 파일에 `__all__` 리스트를 명시하여 외부에 공개할 Public 클래스/함수를 명확히 캡슐화하십시오.
- **PEP 561 Type Marker (`py.typed`)**: mypy, pyright 등 타입 체커가 패키지의 타입 힌팅을 인식할 수 있도록 패키지 루트에 `py.typed` 마커 파일을 **[반드시]** 포함하십시오.
- **Docstring 및 Type Annotations**: 모든 Public API 함수 및 메서드에 Python Type Hinting과 Google/Numpy 스타일의 Docstring을 필수 작성하십시오.

---

## 🧪 3. 패키지 검증 (twine & build)

- **배포 검증**: PyPI 업로드 전 `build` 툴로 파이프라인 산출물(wheel, sdist)을 생성하고 `twine check`를 통해 메타데이터 및 README 렌더링 정상 여부를 확인하십시오.
