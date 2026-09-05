---
name: rule-validator
description: agent-rules-template의 배포 원본을 build 전에 검사하고, build 후 bundle·metadata·원본 동기화를 기계적으로 검증할 때 사용합니다. 규칙 의미 진단은 명시적 요청이 있거나 규범적 의미 변경의 주된 위험을 기계 검증만으로 확인할 수 없을 때 build 전에 수행합니다.
---

# Rule Validator Skill

이 스킬은 `rules/`, `guides/`, `skills/`, `subagents/` 원본과 배포 bundle의 기계적 무결성을 검증합니다. 파일을 편집할 때마다 반복하지 않고, 배포 대상 변경을 하나의 논리적 작업 단위로 마무리할 때 한 번 활성화합니다.

---

## 실행 흐름

1. 원본 변경이 안정되면 필요한 경우에만 build 전 의미 진단을 수행합니다.
2. source preflight를 실행합니다.
3. preflight가 통과하면 bundle을 build합니다.
4. 생성된 artifact를 검증합니다.
5. 변경 유형에 해당하는 테스트를 실행합니다.

```bash
python .agents/skills/rule-validator/scripts/validate_rules.py --pre-build
python scripts/build_dist.py
python .agents/skills/rule-validator/scripts/validate_rules.py --post-build
```

`uv run python`, `python3`, `py` 등 프로젝트와 실행 환경에서 사용 가능한 Python 3 명령으로 대체할 수 있습니다. Python 런타임이 없으면 정적 검사를 성공으로 간주하지 말고 미검증 상태와 이유를 보고합니다.

검증 후 검사 대상 원본이 다시 변경되면 pre-build부터 다시 실행합니다. post-build 오류만 수정했고 원본이 바뀌지 않았다면 필요한 build 또는 post-build 검사만 반복합니다.

## Source Preflight

`--pre-build`는 bundle의 현재 상태와 무관하게 다음 원본 계약을 차단형으로 검사합니다.

- 필수 Core 모듈과 배포 rule category
- UTF-8 인코딩과 금지된 생략 표현
- public skill과 subagent의 YAML frontmatter
- 원본 Markdown 상대 링크
- `AGENTS.md`, `pyproject.toml`, `README.md`, `CHANGELOG.md`의 version 정합성

## Artifact Verification

`--post-build`는 build가 성공한 뒤 다음 생성 결과를 차단형으로 검사합니다.

- bundle Markdown의 인코딩, frontmatter, 금지 표현과 상대 링크
- bundle metadata와 managed file hash 계약
- bundle metadata의 version 정합성
- 임시 canonical build와 현재 bundle의 파일 집합 및 byte 내용 일치

인자 없이 실행하면 호환성을 위해 source와 artifact를 모두 검사합니다. 일반 유지보수 흐름에서는 시점이 명확한 `--pre-build`와 `--post-build`를 사용합니다.

검사 실패 시 보고된 파일과 원인을 수정하고 해당 검사부터 다시 실행합니다. 실패를 성공으로 보고하거나 정규식을 수작업으로 대신 계산하지 않습니다.

## Build 전 의미적 정합성 권고 진단

의미 진단은 기계 검증의 자동 후속 단계가 아닙니다. 사용자가 의미 감사·검수를 요청했거나 authority, precedence, scope, Hard Rule 등 규범적 의미 변경의 주된 위험을 기계 검증만으로 확인할 수 없는 경우에만, 원본 변경이 안정된 뒤 build 전에 [의미 진단 rubric](references/semantic-audit.md)을 읽고 수행합니다.

같은 변경에 독립 검토도 요구되는 경우에는 의미 진단을 별도로 반복하지 않고, 해당 rubric과 검증 증거를 독립 검토의 입력으로 사용합니다.

의미 진단 결과는 build를 차단하는 기계 오류가 아닌 advisory로 보고합니다. 진단 결과로 원본을 수정했다면 source preflight부터 다시 실행합니다. build 후에는 생성 과정이 규칙 의미를 바꿨다는 구체적 증거가 없는 한 의미 진단을 반복하지 않습니다.
