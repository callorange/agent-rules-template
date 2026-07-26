#!/usr/bin/env python3
"""
validate_rules.py - rules/ 및 dist/ 내 규칙 모듈의 정적 무결성을 검증하는 도구.
"""

import os
import re
import sys
from pathlib import Path

# 프로젝트 루트 디렉터리 설정
ROOT_DIR = Path(__file__).resolve().parent.parent
RULES_DIR = ROOT_DIR / "rules"
DIST_DIR = ROOT_DIR / "dist"

# 1. 필수 코어 모듈 목록
REQUIRED_CORE_FILES = [
    "rules/core/base.md",
    "rules/core/workflow.md",
    "rules/core/integrity.md",
    "rules/core/standards.md",
]

# 2. 금지된 출력 생략 표현 패턴
FORBIDDEN_PATTERNS = [
    (re.compile(r"\.\.\.\s*\(중략\)\s*\.\.\."), "... (중략) ..."),
    (re.compile(r"//\s*기존\s*(내용|코드)\s*와?\s*동일"), "// 기존 내용과 동일"),
    (re.compile(r"\[나머지\s*부분\s*생략\]"), "[나머지 부분 생략]"),
    (re.compile(r"\(이전\s*코드는\s*위와\s*같음\)"), "(이전 코드는 위와 같음)"),
]

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

    # [text](relative_path) 패턴 매칭 (http/https/mailto/file 등 외의 로컬 상대 경로 대상)
    link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    for idx, line in enumerate(content.splitlines(), 1):
        for match in link_pattern.finditer(line):
            target = match.group(2).strip()
            # 외부 URL, 앵커 링크 및 file:/// 스키마 제외
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

def main():
    all_errors = []

    print("🔍 [rule-validator] 규칙 모듈 무결성 검증을 시작합니다...\n")

    # 1. 필수 코어 모듈 존재 여부 검사
    print("1️⃣ 필수 코어 모듈 검사 중...")
    for req_file in REQUIRED_CORE_FILES:
        full_path = ROOT_DIR / req_file
        if not full_path.exists():
            all_errors.append(f"필수 코어 모듈 누락: '{req_file}' 파일이 존재하지 않습니다.")

    # 2. rules/ 및 dist/ 내 모든 .md 파일 수집
    md_files = list(RULES_DIR.glob("**/*.md"))
    if DIST_DIR.exists():
        md_files.extend(DIST_DIR.glob("**/*.md"))
    
    root_agents = ROOT_DIR / "AGENTS.md"
    if root_agents.exists():
        md_files.append(root_agents)

    print(f"2️⃣ 총 {len(md_files)}개 Markdown 파일 인코딩 및 금지 표현 검사 중...")
    for md_file in md_files:
        errs = check_encoding_and_content(md_file)
        all_errors.extend(errs)

    print(f"3️⃣ Markdown 내부 로컬 상대 링크 유효성 검사 중...")
    for md_file in md_files:
        errs = check_markdown_links(md_file)
        all_errors.extend(errs)

    print("\n" + "=" * 50)
    if all_errors:
        print(f"❌ 검증 실패: 총 {len(all_errors)}개의 오류가 발견되었습니다.")
        for err in all_errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("✅ 모든 규칙 모듈 및 Markdown 파일 검증을 성공적으로 통과하였습니다!")
        sys.exit(0)

if __name__ == "__main__":
    main()
