#!/usr/bin/env python3
"""
validate_rules.py - rules/, guides/, skills/, subagents/ 원본 및 dist/ 배포 아티팩트의 정적 무결성을 검증하는 도구.
(rule-validator 스킬 전용 헬퍼 스크립트)
"""

import importlib.util
import json
import re
import shutil
import sys
from pathlib import Path

# 프로젝트 루트 디렉터리 설정 (.agents/skills/rule-validator/scripts/ -> 프로젝트 루트)
ROOT_DIR = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT_DIR))
RULES_DIR = ROOT_DIR / "rules"
GUIDES_DIR = ROOT_DIR / "guides"
SKILLS_DIR = ROOT_DIR / "skills"
SUBAGENTS_DIR = ROOT_DIR / "subagents"
BUNDLE_DIR = ROOT_DIR / "agent_rules_template" / "bundle"
from agent_rules_template.scripts.sync import validate_bundle  # noqa: E402

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
        or relative.parts[:4] == ("agent_rules_template", "bundle", ".agents", "agents")
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

def load_build_module():
    """배포 build 모듈을 단일 경로에서 로드합니다."""
    build_script = ROOT_DIR / "scripts" / "build_dist.py"
    spec = importlib.util.spec_from_file_location("rule_validator_build_dist", build_script)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"배포 빌드 스크립트를 불러올 수 없습니다: {build_script}")
    build_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build_module)
    return build_module


def check_source_layout() -> list:
    """필수 Core 및 rule 카테고리의 build 포함 여부를 검사합니다."""
    try:
        load_build_module().validate_source_layout()
    except (OSError, RuntimeError, ValueError) as error:
        return [f"[source layout] {error}"]
    return []


def check_version_coherence(root_dir: Path = ROOT_DIR, bundle_dir: Path = BUNDLE_DIR) -> list:
    """배포 버전 원본과 동기화 대상의 일치 여부를 검사합니다."""
    errors = []
    try:
        agents_text = (root_dir / "AGENTS.md").read_text(encoding="utf-8")
        agents_match = re.search(r"\*\*Version\*\*:\s*([^|\n]+)", agents_text)
        if agents_match is None:
            return ["[version] AGENTS.md에서 Version을 찾을 수 없습니다."]
        expected = agents_match.group(1).strip()

        pyproject_text = (root_dir / "pyproject.toml").read_text(encoding="utf-8")
        project_match = re.search(
            r"(?ms)^\[project\]\s*$.*?^version\s*=\s*[\"']([^\"']+)[\"']",
            pyproject_text,
        )
        readme_text = (root_dir / "README.md").read_text(encoding="utf-8")
        readme_match = re.search(r"현재 버전은 \*\*([^*]+)\*\*", readme_text)
        metadata = json.loads((bundle_dir / "metadata.json").read_text(encoding="utf-8"))
        changelog_text = (root_dir / "CHANGELOG.md").read_text(encoding="utf-8")

        declared = {
            "pyproject.toml": project_match.group(1) if project_match else None,
            "README.md": readme_match.group(1).strip() if readme_match else None,
            "bundle/metadata.json": metadata.get("template_version"),
        }
        for source, value in declared.items():
            if value != expected:
                errors.append(
                    f"[version] {source}의 버전 {value!r}이 AGENTS.md의 {expected!r}과 일치하지 않습니다."
                )
        if not re.search(rf"(?m)^## \[{re.escape(expected)}\](?:\s|$)", changelog_text):
            errors.append(f"[version] CHANGELOG.md에 [{expected}] 버전 구획이 없습니다.")
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        errors.append(f"[version] 버전 정합성 검사 실패: {error}")
    return errors


def check_dist_freshness() -> list:
    """임시 경로에 생성한 bundle과 committed bundle의 최신성을 비교합니다."""
    errors = []
    try:
        build_module = load_build_module()
    except (OSError, RuntimeError) as error:
        return [f"[dist freshness] {error}"]

    # Windows sandbox에서도 접근 가능한 프로젝트 전용 작업 경로를 사용합니다.
    work_dir = ROOT_DIR / ".rule-validator-build"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    try:
        generated_dir = work_dir / "bundle"
        build_module.build_dist(generated_dir)
        generated_files = {
            path.relative_to(generated_dir)
            for path in generated_dir.rglob("*") if path.is_file()
        }
        committed_files = {
            path.relative_to(BUNDLE_DIR)
            for path in BUNDLE_DIR.rglob("*") if path.is_file()
        } if BUNDLE_DIR.exists() else set()
        missing = sorted(generated_files - committed_files)
        unexpected = sorted(committed_files - generated_files)
        stale = sorted(
            relative for relative in generated_files & committed_files
            if (generated_dir / relative).read_bytes() != (BUNDLE_DIR / relative).read_bytes()
        )
    finally:
        if work_dir.exists():
            shutil.rmtree(work_dir)

    differences = []
    if missing:
        differences.append("누락: " + ", ".join(str(path) for path in missing))
    if unexpected:
        differences.append("예상 밖: " + ", ".join(str(path) for path in unexpected))
    if stale:
        differences.append("내용 불일치: " + ", ".join(str(path) for path in stale))
    if differences:
        errors.append("bundle 배포 아티팩트가 현재 원본과 일치하지 않습니다 (" + "; ".join(differences) + "). 'python scripts/build_dist.py'를 실행하여 최신화하십시오.")

    return errors


def check_dist_metadata() -> list:
    """원본 layout을 해석하지 않고 bundle 계약을 검증합니다."""
    if not BUNDLE_DIR.exists():
        return ["bundle 디렉터리가 존재하지 않습니다."]
    try:
        validate_bundle(BUNDLE_DIR)
    except (OSError, ValueError, KeyError) as error:
        return [f"[dist metadata] {error}"]
    return []

def main():
    all_errors = []

    print("🔍 [rule-validator] 원본 및 dist/ 배포 아티팩트 무결성 검증을 시작합니다...\n")

    # 1. 필수 Core 및 배포 카테고리 계약 검사
    print("1️⃣ 필수 Core 및 rule 카테고리 배포 계약 검사 중...")
    all_errors.extend(check_source_layout())

    # 2. rules/, guides/, skills/, subagents/ 원본 SSOT 마크다운 파일 동적 수집
    md_files = list(RULES_DIR.glob("**/*.md"))
    if GUIDES_DIR.exists():
        md_files.extend(GUIDES_DIR.glob("**/*.md"))
    if SKILLS_DIR.exists():
        md_files.extend(SKILLS_DIR.glob("**/*.md"))
    if SUBAGENTS_DIR.exists():
        md_files.extend(SUBAGENTS_DIR.glob("**/*.md"))
    
    root_agents = ROOT_DIR / "AGENTS.md"
    if root_agents.exists():
        md_files.append(root_agents)

    # 3. bundle 배포 아티팩트 디렉터리 내 마크다운 파일 동적 수집
    if BUNDLE_DIR.exists():
        dist_md_files = list(BUNDLE_DIR.glob("**/*.md"))
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

    # 5. dist metadata, version coherence, and freshness
    print(f"5️⃣ bundle metadata 계약 검사 중...")
    all_errors.extend(check_dist_metadata())
    print(f"6️⃣ 배포 버전 정합성 검사 중...")
    all_errors.extend(check_version_coherence())
    print(f"7️⃣ bundle 배포 아티팩트 최신 동기화 상태 검사 중...")
    all_errors.extend(check_dist_freshness())

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
