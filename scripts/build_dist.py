#!/usr/bin/env python3
"""
scripts/build_dist.py
AI 에이전트 및 개발자를 위한 dist/ 배포 아티팩트 자동 조립 스크립트.
rules/, skills/, subagents/ 의 원본 모듈들을 읽어 고품질 dist/AGENTS.md, dist/rules/ 및 dist/.agents/ 구조를 생성합니다.
"""

import os
import re
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RULES_DIR = PROJECT_ROOT / "rules"
SKILLS_DIR = PROJECT_ROOT / "skills"
SUBAGENTS_DIR = PROJECT_ROOT / "subagents"

DIST_DIR = PROJECT_ROOT / "dist"
DIST_RULES_DIR = DIST_DIR / "rules"
DIST_AGENTS_DIR = DIST_DIR / ".agents"
DIST_AGENTS_SKILLS_DIR = DIST_AGENTS_DIR / "skills"
DIST_AGENTS_AGENTS_DIR = DIST_AGENTS_DIR / "agents"

CORE_ORDER = [
    "base.md",
    "workflow.md",
    "integrity.md",
    "standards.md",
    "hidden-knowledge.md"
]

CATEGORY_METADATA = {
    "architecture": ("🏛️ 도메인 및 아키텍처 규칙", "Architecture & Domain Rules"),
    "frameworks": ("🛠️ 프레임워크 특화 규칙", "Framework Specific Rules"),
    "packaging": ("📦 패키징 및 배포 생태계 규칙", "Packaging & Ecosystem Rules"),
    "styles": ("🎨 언어별 코딩 스타일 가이드 (Google Style Guides)", "Language Style Guides")
}

def extract_title_and_description(file_path: Path) -> tuple[str, str]:
    """마크다운 파일에서 최상단 H1 제목과 첫 문장을 추출합니다."""
    content = file_path.read_text(encoding="utf-8")
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    
    title = file_path.name
    desc = ""
    
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            # 괄호 안 영문/한글 요약 정제
            title = re.sub(r'\(.*?\)', '', title).strip()
            break
            
    for line in lines:
        if not line.startswith("#") and not line.startswith("---") and not line.startswith("-"):
            desc = line
            break
            
    return title, desc

def build_dist():
    print("🚀 Starting dist/ bundle assembly...")

    # 1. dist 디렉토리 초기화 (Clean Build)
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    DIST_RULES_DIR.mkdir(parents=True, exist_ok=True)

    # 2. dist/AGENTS.md 헤더 생성
    agents_md_content = [
        "# AGENTS.md - Unified Agent Execution Rules & Governance",
        "",
        "본 문서는 `agents-template`에서 `scripts/build_dist.py` 스크립트를 통해 자동으로 조립 생성된 **최상위 AI 에이전트 통합 실행 지침 및 거버넌스(Governance) 문서**입니다.",
        "프로젝트에 참여하는 모든 AI 에이전트는 본 문서의 헌법적 원칙과 핵심 행동 규약을 최우선으로 준수해야 합니다.",
        "",
        "---",
        ""
    ]

    # 3. rules/core/* 파일 순서대로 병합
    core_dir = RULES_DIR / "core"
    for filename in CORE_ORDER:
        core_file = core_dir / filename
        if core_file.exists():
            print(f"  + Merging core module: {filename}")
            file_text = core_file.read_text(encoding="utf-8").strip()
            agents_md_content.append(file_text)
            agents_md_content.append("\n---\n")
        else:
            print(f"  ⚠️ Warning: Core file {filename} not found!")

    # 4. On-Demand 기술 스택 링킹 섹션 동적 생성
    agents_md_content.append("## 📚 기술 스택별 특화 및 온디맨드 규칙 모듈 (Read-on-Demand)")
    agents_md_content.append("")
    agents_md_content.append("프로젝트의 구체적인 기술 스택, 배포 환경 및 언어 스타일 가이드는 필요 시 아래 전용 모듈 문서를 참조(Read-on-Demand)하십시오.")
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
    final_agents_md_path = DIST_DIR / "AGENTS.md"
    final_agents_md_path.write_text("\n".join(agents_md_content).strip() + "\n", encoding="utf-8")
    print(f"✅ Generated: {final_agents_md_path}")

    # 6. rules/architecture, packaging, styles 디렉토리를 dist/rules/ 아래로 복사
    for cat_name in CATEGORY_METADATA.keys():
        src_cat = RULES_DIR / cat_name
        dest_cat = DIST_RULES_DIR / cat_name
        if src_cat.exists():
            shutil.copytree(src_cat, dest_cat)
            print(f"  + Copied category module: {cat_name} -> dist/rules/{cat_name}")

    # 7. skills/ 및 subagents/ 원본 모듈을 dist/.agents/ 디렉터리로 복사 및 패키징
    if SKILLS_DIR.exists():
        DIST_AGENTS_SKILLS_DIR.mkdir(parents=True, exist_ok=True)
        # .gitkeep 제외한 디렉터리/파일 복사
        for item in SKILLS_DIR.iterdir():
            if item.name.startswith("."):
                continue
            dest_item = DIST_AGENTS_SKILLS_DIR / item.name
            if item.is_dir():
                shutil.copytree(item, dest_item)
                print(f"  + Copied distributable skill: {item.name} -> dist/.agents/skills/{item.name}")
            else:
                shutil.copy2(item, dest_item)

    if SUBAGENTS_DIR.exists():
        DIST_AGENTS_AGENTS_DIR.mkdir(parents=True, exist_ok=True)
        for item in SUBAGENTS_DIR.iterdir():
            if item.name.startswith("."):
                continue
            dest_item = DIST_AGENTS_AGENTS_DIR / item.name
            if item.is_dir():
                shutil.copytree(item, dest_item)
            else:
                shutil.copy2(item, dest_item)
            print(f"  + Copied distributable subagent: {item.name} -> dist/.agents/agents/{item.name}")

    print("🎉 dist/ bundle assembly completed successfully!")

if __name__ == "__main__":
    build_dist()
