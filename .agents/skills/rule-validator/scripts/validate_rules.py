#!/usr/bin/env python3
"""
validate_rules.py - rules/, skills/, subagents/ 원본 규칙 모듈 및 dist/ 배포 아티팩트의 정적 무결성을 검증하는 도구.
(rule-validator 스킬 전용 헬퍼 스크립트)
"""

import importlib.util
import re
import sys
import tempfile
from pathlib import Path

# 프로젝트 루트 디렉터리 설정 (.agents/skills/rule-validator/scripts/ -> 프로젝트 루트)
ROOT_DIR = Path(__file__).resolve().parents[4]
RULES_DIR = ROOT_DIR / "rules"
SKILLS_DIR = ROOT_DIR / "skills"
SUBAGENTS_DIR = ROOT_DIR / "subagents"
DIST_DIR = ROOT_DIR / "dist"

# 금지된 출력 생략 표현 패턴
FORBIDDEN_PATTERNS = [
    (re.compile(r"\.\.\.\s*\(중략\)\s*\.\.\."), "... (중략) ..."),
    (re.compile(r"//\s*기존\s*(내용|코드)\s*와?\s*동일"), "// 기존 내용과 동일"),
    (re.compile(r"\[나머지\s*부분\s*생략\]"), "[나머지 부분 생략]"),
    (re.compile(r"\(이전\s*코드는\s*위와\s*같음\)"), "(이전 코드는 위와 같음)"),
]

def check_yaml_frontmatter(file_path: Path) -> list:
    """스킬 및 서브에이전트 파일의 YAML Frontmatter (name, description) 존재 여부를 검사합니다."""
    errors = []
    # 모든 SKILL.md와 공개 subagents 원본·배포본만 대상입니다.
    relative = file_path.relative_to(ROOT_DIR)
    is_public_subagent = (
        relative.parts[:1] == ("subagents",)
        or relative.parts[:3] == ("dist", ".agents", "agents")
    )
    if file_path.name == "SKILL.md" or is_public_subagent:
        try:
            content = file_path.read_text(encoding="utf-8")
            if not re.match(r"\A---\r?\n", content):
                errors.append(f"[{file_path.relative_to(ROOT_DIR)}] YAML Frontmatter 헤더('---')가 누락되었습니다.")
                return errors
            
            closing = re.search(r"(?m)^---\s*$", content[4:])
            if not closing:
                errors.append(f"[{file_path.relative_to(ROOT_DIR)}] YAML Frontmatter 구획이 올바르게 닫히지 않았습니다.")
                return errors

            frontmatter = content[4:][0:closing.start()]
            if not re.search(r"(?m)^name:\s*\S[^\r\n]*$", frontmatter):
                errors.append(f"[{file_path.relative_to(ROOT_DIR)}] YAML Frontmatter에 'name:' 필드가 누락되었습니다.")
            if not re.search(r"(?m)^description:\s*\S[^\r\n]*$", frontmatter):
                errors.append(f"[{file_path.relative_to(ROOT_DIR)}] YAML Frontmatter에 'description:' 필드가 누락되었습니다.")
        except Exception as e:
            errors.append(f"[{file_path.relative_to(ROOT_DIR)}] Frontmatter 검사 에러: {e}")
    return errors

def check_encoding_and_content(file_path: Path) -> list:
    """파일의 UTF-8 인코딩 및 금지 표현을 검사합니다."""
    errors = []
    try:
        content = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        errors.append(f"[{file_path.relative_to(ROOT_DIR)}] 인코딩 오류 (UTF-8 아님): {e}")
        return errors
    except Exception as e:
        errors.append(f"[{file_path.relative_to(ROOT_DIR)}] 파일 읽기 실패: {e}")
        return errors

    # 코드 블록(```...```) 및 인라인 백틱(`...`) 내부의 안내용 예시 구문은 검사 대상에서 제외
    content_clean = re.sub(r"```[\s\S]*?```", "", content)
    content_clean = re.sub(r"`[^`\n]+`", "", content_clean)

    # 금지 표현 검사
    lines = content_clean.splitlines()
    for idx, line in enumerate(lines, 1):
        for pattern, label in FORBIDDEN_PATTERNS:
            if pattern.search(line):
                errors.append(
                    f"[{file_path.relative_to(ROOT_DIR)}:{idx}] 금지된 생략 표현 발견: '{label}'"
                )
    return errors

def check_markdown_links(file_path: Path) -> list:
    """Markdown 파일 내 상대 경로 링크의 실존 여부를 검사합니다."""
    errors = []
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return errors  # 인코딩 검사에서 이미 포착됨

    # 코드 블록 및 인라인 백틱 내부 예시 링크 제외
    content_clean = re.sub(r"```[\s\S]*?```", "", content)
    content_clean = re.sub(r"`[^`\n]+`", "", content_clean)

    # 선택적 제목과 <angle target>을 지원하는 Markdown 링크를 검사합니다.
    link_pattern = re.compile(r"\[[^\]]+\]\(\s*(<[^>]+>|[^\s)]+)(?:\s+(?:\"[^\"]*\"|'[^']*'))?\s*\)")
    for idx, line in enumerate(content_clean.splitlines(), 1):
        for match in link_pattern.finditer(line):
            target = match.group(1).strip().strip("<>")
            # 외부 URL, 앵커 링크 및 file: 스키마 제외
            if target.startswith(("http://", "https://", "mailto:", "#", "file:")):
                continue
            
            # 앵커 부분 제거 (예: path/file.md#section -> path/file.md)
            clean_target = target.split("#")[0]
            if not clean_target:
                continue

            target_path = (file_path.parent / clean_target).resolve()
            if not target_path.exists():
                errors.append(
                    f"[{file_path.relative_to(ROOT_DIR)}:{idx}] 깨진 링크 발견: '{target}' -> 경로에 파일 없음 ({target_path})"
                )
    return errors

def check_dist_freshness() -> list:
    """임시 경로에 결정적으로 생성한 번들과 committed dist의 내용을 비교합니다."""
    warnings = []
    build_script = ROOT_DIR / "scripts" / "build_dist.py"
    spec = importlib.util.spec_from_file_location("build_dist", build_script)
    if spec is None or spec.loader is None:
        return [f"[경고] dist 최신성 비교를 위한 빌드 스크립트를 불러올 수 없습니다: {build_script}"]
    build_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build_module)

    # 격리 환경에서도 쓰기 가능한 프로젝트 내부 임시 디렉터리를 사용하며, 종료 시 제거합니다.
    with tempfile.TemporaryDirectory(dir=ROOT_DIR) as temp_dir:
        generated_dir = Path(temp_dir) / "dist"
        build_module.build_dist(generated_dir)
        generated_files = {
            path.relative_to(generated_dir)
            for path in generated_dir.rglob("*") if path.is_file()
        }
        committed_files = {
            path.relative_to(DIST_DIR)
            for path in DIST_DIR.rglob("*") if path.is_file()
        } if DIST_DIR.exists() else set()
        missing = sorted(generated_files - committed_files)
        unexpected = sorted(committed_files - generated_files)
        stale = sorted(
            relative for relative in generated_files & committed_files
            if (generated_dir / relative).read_bytes() != (DIST_DIR / relative).read_bytes()
        )

    differences = []
    if missing:
        differences.append("누락: " + ", ".join(str(path) for path in missing))
    if unexpected:
        differences.append("예상 밖: " + ", ".join(str(path) for path in unexpected))
    if stale:
        differences.append("내용 불일치: " + ", ".join(str(path) for path in stale))
    if differences:
        warnings.append("[경고] dist/ 배포 아티팩트가 현재 원본과 일치하지 않습니다 (" + "; ".join(differences) + "). 'python scripts/build_dist.py'를 실행하여 최신화하십시오.")

    return warnings

def main():
    all_errors = []

    print("🔍 [rule-validator] 원본 및 dist/ 배포 아티팩트 무결성 검증을 시작합니다...\n")

    # 1. 필수 코어 최상위 모듈 및 디렉터리 동적 탐색 검사
    print("1️⃣ 필수 코어 모듈 동적 탐색 및 검사 중...")
    core_dir = RULES_DIR / "core"
    if not core_dir.exists():
        all_errors.append("코어 디렉터리 누락: 'rules/core' 디렉터리가 존재하지 않습니다.")
    else:
        core_files = sorted(list(core_dir.glob("*.md")))
        base_file = core_dir / "01-base.md"
        if not base_file.is_file():
            all_errors.append("필수 최상위 헌법 모듈 누락: 정확한 파일명 'rules/core/01-base.md'가 존재하지 않습니다.")
        else:
            print(f"   (동적 탐색된 코어 모듈 {len(core_files)}개: {[f.name for f in core_files]})")

    # 2. rules/, skills/, subagents/ 원본 SSOT 마크다운 파일 동적 수집
    md_files = list(RULES_DIR.glob("**/*.md"))
    if SKILLS_DIR.exists():
        md_files.extend(SKILLS_DIR.glob("**/*.md"))
    if SUBAGENTS_DIR.exists():
        md_files.extend(SUBAGENTS_DIR.glob("**/*.md"))
    
    root_agents = ROOT_DIR / "AGENTS.md"
    if root_agents.exists():
        md_files.append(root_agents)

    # 3. dist/ 배포 아티팩트 디렉터리 내 마크다운 파일 동적 수집
    if DIST_DIR.exists():
        dist_md_files = list(DIST_DIR.glob("**/*.md"))
        md_files.extend(dist_md_files)
        print(f"2️⃣ 총 {len(md_files)}개 원본 및 dist/ 배포 Markdown 파일 검사 대상 수집 완료 (dist/ {len(dist_md_files)}개 포함)")
    else:
        print(f"2️⃣ 총 {len(md_files)}개 원본 Markdown 파일 검사 대상 수집 완료")

    # 3. YAML Frontmatter, 인코딩, 금지 표현 및 상대 링크 검사
    print(f"3️⃣ YAML Frontmatter, UTF-8 인코딩 및 금지 표현 검사 중...")
    for md_file in md_files:
        errs = check_yaml_frontmatter(md_file)
        all_errors.extend(errs)
        errs = check_encoding_and_content(md_file)
        all_errors.extend(errs)

    print(f"4️⃣ Markdown 내부 로컬 상대 링크 유효성 검사 중...")
    for md_file in md_files:
        errs = check_markdown_links(md_file)
        all_errors.extend(errs)

    # 5. dist/ 최신 동기화 경고 검사
    print(f"5️⃣ dist/ 배포 아티팩트 최신 동기화 상태 검사 중...")
    dist_warnings = check_dist_freshness()
    for warn in dist_warnings:
        print(f"   {warn}")

    print("\n" + "=" * 50)
    if all_errors:
        print(f"❌ 검증 실패: 총 {len(all_errors)}개의 에러가 발견되었습니다.")
        for err in all_errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("✅ 모든 원본 규칙 모듈, dist/ 배포 아티팩트 및 Markdown 파일 검증을 성공적으로 통과하였습니다!")
        sys.exit(0)

if __name__ == "__main__":
    main()
