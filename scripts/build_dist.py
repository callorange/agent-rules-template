#!/usr/bin/env python3
"""
scripts/build_dist.py
AI 에이전트 및 개발자를 위한 bundle 배포 아티팩트 자동 조립 스크립트.

⚠️ [헌법 가드: 내부 vs 배포 아티팩트 격리]
이 레포지토리 자체의 개발·유지보수 전용 메타 스킬/서브에이전트인 `/.agents/` 디렉터리는 절대 dist/ 에 direct 복사되지 않습니다.
배포 아티팩트는 공용 원본인 `/skills/` 및 `/subagents/` 에서만 읽어 타 프로젝트 호환 구조(`dist/.agents/`)로 패키징됩니다.
"""

import re
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agent_rules_template.scripts.common import (
    BINARY_HASH_POLICY,
    END_MARKER,
    SCHEMA_VERSION,
    START_MARKER,
    TEXT_HASH_POLICY,
    file_record,
    logical_path,
    managed_block_hash,
    write_json,
)

RULES_DIR = PROJECT_ROOT / "rules"
GUIDES_DIR = PROJECT_ROOT / "guides"
SKILLS_DIR = PROJECT_ROOT / "skills"
SUBAGENTS_DIR = PROJECT_ROOT / "subagents"

BUNDLE_DIR = PROJECT_ROOT / "agent_rules_template" / "bundle"

CATEGORY_METADATA = {
    "architecture": ("🏛️ 도메인 및 아키텍처 규칙", "Architecture & Domain Rules"),
    "frameworks": ("🛠️ 프레임워크 특화 규칙", "Framework Specific Rules"),
    "packaging": ("📦 패키징 및 배포 생태계 규칙", "Packaging & Ecosystem Rules"),
    "styles": ("🎨 언어별 코딩 스타일 가이드 (Google Style Guides)", "Language Style Guides")
}
REQUIRED_CORE_FILES = {
    "01-base.md",
    "02-workflow.md",
    "03-integrity.md",
    "04-standards.md",
    "05-docs-maintenance.md",
}
SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")


def template_version() -> str:
    """저장소 헌법의 버전을 bundle version으로 사용합니다."""
    content = (PROJECT_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    match = re.search(r"\*\*Version\*\*:\s*([^|\n]+)", content)
    if match is None:
        raise ValueError("AGENTS.md에서 '**Version**' 값을 찾을 수 없습니다.")
    version = match.group(1).strip()
    if not SEMVER_PATTERN.fullmatch(version):
        raise ValueError(f"AGENTS.md의 Version이 유효한 SemVer가 아닙니다: {version!r}")
    return version


def validate_source_layout(rules_dir: Path | None = None) -> None:
    """필수 Core 및 배포 카테고리가 build 설정과 일치하는지 검증합니다."""
    source_rules = rules_dir if rules_dir is not None else RULES_DIR
    core_dir = source_rules / "core"
    if not core_dir.is_dir():
        raise ValueError("필수 디렉터리 'rules/core'가 존재하지 않습니다.")

    missing_core = sorted(
        name for name in REQUIRED_CORE_FILES if not (core_dir / name).is_file()
    )
    if missing_core:
        raise ValueError("필수 Core 모듈 누락: " + ", ".join(missing_core))

    actual_categories = {
        path.name for path in source_rules.iterdir()
        if path.is_dir() and path.name != "core" and not path.name.startswith(".")
    }
    configured_categories = set(CATEGORY_METADATA)
    missing_categories = sorted(configured_categories - actual_categories)
    unknown_categories = sorted(actual_categories - configured_categories)
    problems = []
    if missing_categories:
        problems.append("설정된 카테고리 디렉터리 누락: " + ", ".join(missing_categories))
    if unknown_categories:
        problems.append("build 설정에 없는 rule 카테고리: " + ", ".join(unknown_categories))
    if problems:
        raise ValueError("; ".join(problems))


def build_metadata(bundle_dir: Path) -> None:
    """완성된 bundle의 canonical ownership metadata를 작성합니다."""
    managed_files: dict[str, dict[str, str]] = {}
    normalized_paths: set[str] = set()
    for path in sorted(bundle_dir.rglob("*")):
        relative_path = path.relative_to(bundle_dir)
        if not path.is_file() or relative_path in {Path("AGENTS.md"), Path("metadata.json")}:
            continue
        relative = logical_path(relative_path)
        if relative != relative_path.as_posix():
            raise ValueError(f"NFC가 아닌 bundle 경로: {relative_path}")
        if relative in normalized_paths:
            raise ValueError(f"NFC-normalized distribution path collision: {relative}")
        normalized_paths.add(relative)
        managed_files[relative] = file_record(path)
    agents = bundle_dir / "AGENTS.md"
    write_json(bundle_dir / "metadata.json", {
        "schema_version": SCHEMA_VERSION,
        "template_version": template_version(),
        "hash_policy": {"text": TEXT_HASH_POLICY, "binary": BINARY_HASH_POLICY},
        "managed_block": {
            "file": "AGENTS.md",
            "start_marker": START_MARKER,
            "end_marker": END_MARKER,
            "sha256": managed_block_hash(agents),
        },
        "managed_files": managed_files,
    })

def extract_title_and_description(file_path: Path) -> tuple[str, str]:
    """마크다운 파일에서 최상단 H1 제목과 첫 문장을 추출합니다."""
    content = file_path.read_text(encoding="utf-8")
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    
    title = file_path.name
    desc = ""
    
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break
            
    for line in lines:
        if not line.startswith("#") and not line.startswith("---") and not line.startswith("-"):
            desc = line
            break
            
    return title, desc

def build_dist(output_dir: Path | None = None):
    """단일 canonical bundle을 생성하고 필요하면 지정 경로에 생성합니다."""
    validate_source_layout()
    template_version()
    # metadata만 NFC로 바뀌는 불일치를 기존 bundle 제거 전에 차단합니다.
    for source in (RULES_DIR, GUIDES_DIR, SKILLS_DIR, SUBAGENTS_DIR):
        for path in source.rglob("*"):
            relative = path.relative_to(source)
            if logical_path(relative) != relative.as_posix():
                raise ValueError(f"NFC가 아닌 source 경로: {path}")
    dist_dir = output_dir if output_dir is not None else BUNDLE_DIR
    dist_rules_dir = dist_dir / "rules"
    dist_guides_dir = dist_dir / "guides"
    dist_agents_skills_dir = dist_dir / ".agents" / "skills"
    dist_agents_agents_dir = dist_dir / ".agents" / "agents"

    print("🚀 Starting dist/ bundle assembly...")

    # 1. dist 디렉토리 초기화 (Clean Build)
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True, exist_ok=True)
    dist_rules_dir.mkdir(parents=True, exist_ok=True)

    # 2. dist/AGENTS.md 헤더 생성
    agents_md_content = [
        START_MARKER,
        "",
        "# AGENTS.md - Unified Agent Execution Rules & Governance",
        "",
        "본 문서는 `agents-template`에서 `scripts/build_dist.py` 스크립트를 통해 자동으로 조립 생성된 **최상위 AI 에이전트 통합 실행 지침 및 거버넌스(Governance) 문서**입니다.",
        "프로젝트에 참여하는 모든 AI 에이전트는 본 문서의 헌법적 원칙과 핵심 행동 규약을 최우선으로 준수해야 합니다.",
        "",
        "---",
        ""
    ]

    # 3. rules/core/* 마크다운 파일 동적 수집 및 병합 (01-, 02- 숫자 접두사 순서 보장)
    core_dir = RULES_DIR / "core"
    if core_dir.exists():
        ordered_core_files = sorted(core_dir.glob("*.md"))
        for core_file in ordered_core_files:
            print(f"  + Merging core module: {core_file.name}")
            file_text = core_file.read_text(encoding="utf-8").strip()
            # rules/core/ 에 작성된 상위 카테고리 마크다운 상대 경로 정제 (../architecture/ -> rules/architecture/)
            file_text = file_text.replace("../architecture/", "rules/architecture/")
            # 통합 AGENTS.md 안에서는 Core 형제 문서의 section 링크를 동일 문서 anchor로 변환
            for sibling_core_file in ordered_core_files:
                file_text = file_text.replace(f"({sibling_core_file.name}#", "(#")
            agents_md_content.append(file_text)
            agents_md_content.append("\n---\n")
    else:
        print("  ⚠️ Warning: rules/core directory not found!")

    # 4. On-Demand 기술 스택 링킹 섹션 동적 생성
    agents_md_content.append("## 📚 기술 스택별 특화 및 온디맨드 규칙 모듈 (Read-on-Demand)")
    agents_md_content.append("")
    agents_md_content.append("위 Core 활성화 계약에 따라 현재 작업과 일치하는 언어, framework, architecture 및 packaging 모듈을 아래 목록에서 선택해 누적 적용하십시오.")
    agents_md_content.append("")

    for cat_name, (cat_title_kr, _) in CATEGORY_METADATA.items():
        cat_dir = RULES_DIR / cat_name
        if not cat_dir.exists():
            continue

        agents_md_content.append(f"### {cat_title_kr}")
        
        # 파일 목록 순서 정렬
        files = sorted(cat_dir.glob("*.md"))
        for f in files:
            rel_path = f"rules/{cat_name}/{f.name}"
            title, _ = extract_title_and_description(f)
            agents_md_content.append(f"- [{f.name}]({rel_path}): {title}")
        
        agents_md_content.append("")

    # 5. dist/AGENTS.md 저장
    final_agents_md_path = dist_dir / "AGENTS.md"
    agents_md_content.extend([
        "",
        "---",
        "",
        "## Template Managed Content",
        "",
        "- 이 Managed Block은 직접 수정하지 마십시오.",
        "- Template이 managed로 설치한 파일을 직접 수정하거나 formatter, fixer, code action으로 자동 변경하지 마십시오.",
        "- 프로젝트별 규칙·예외는 Managed Block 밖의 `Project Rules` 또는 Project-owned rule 파일에 작성하십시오.",
        "- Template과 다른 동작은 managed 규칙을 바꾸지 말고 더 구체적인 Project Rule로 override하십시오.",
        "- 실제 managed 파일 ownership은 이 문서의 목록이 아니라 설치 metadata를 기준으로 합니다.",
        "",
        END_MARKER,
    ])
    final_agents_md_path.write_text("\n".join(agents_md_content).strip() + "\n", encoding="utf-8")
    print(f"✅ Generated: {final_agents_md_path}")

    # 6. rules/architecture, packaging, styles 디렉토리를 dist/rules/ 아래로 복사
    for cat_name in CATEGORY_METADATA.keys():
        src_cat = RULES_DIR / cat_name
        dest_cat = dist_rules_dir / cat_name
        if src_cat.exists():
            shutil.copytree(src_cat, dest_cat)
            print(f"  + Copied category module: {cat_name} -> dist/rules/{cat_name}")

    # 7. 비규범적 설계 참고 자료를 dist/guides/로 1:1 복사합니다.
    # 이 파일들은 dist/AGENTS.md에 병합하지 않으며, 필요할 때만 선택적으로 참조합니다.
    if GUIDES_DIR.exists():
        shutil.copytree(GUIDES_DIR, dist_guides_dir)
        print("  + Copied optional guides -> dist/guides")

    # 8. 공용 배포용 원본(skills/, subagents/)을 타 프로젝트 배포용 구조(dist/.agents/skills/, dist/.agents/agents/)로 패키징
    # (주의: 이 프로젝트 자체의 내부 전용 메타 디렉터리 PROJECT_ROOT/.agents 는 절대 가져오지 않음)
    if SKILLS_DIR.exists():
        dist_agents_skills_dir.mkdir(parents=True, exist_ok=True)
        for item in SKILLS_DIR.iterdir():
            if item.name.startswith("."):
                continue
            dest_item_agents = dist_agents_skills_dir / item.name
            if item.is_dir():
                shutil.copytree(item, dest_item_agents)
                print(f"  + Packaged public skill: {item.name} -> dist/.agents/skills/{item.name}")
            else:
                shutil.copy2(item, dest_item_agents)
                print(f"  + Packaged public skill file: {item.name} -> dist/.agents/skills/{item.name}")

    if SUBAGENTS_DIR.exists():
        dist_agents_agents_dir.mkdir(parents=True, exist_ok=True)
        for item in SUBAGENTS_DIR.iterdir():
            if item.name.startswith("."):
                continue
            dest_item = dist_agents_agents_dir / item.name
            if item.is_dir():
                shutil.copytree(item, dest_item)
            else:
                shutil.copy2(item, dest_item)
            print(f"  + Packaged public subagent: {item.name} -> dist/.agents/agents/{item.name}")

    build_metadata(dist_dir)
    print(f"✅ Generated: {dist_dir / 'metadata.json'}")
    print("🎉 dist/ bundle assembly completed successfully!")

if __name__ == "__main__":
    build_dist()
