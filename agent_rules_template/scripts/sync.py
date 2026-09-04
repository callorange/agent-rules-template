"""번들 metadata만 사용해 소비 프로젝트를 안전하게 동기화합니다."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

from .common import (
    BINARY_HASH_POLICY,
    END_MARKER,
    SCHEMA_VERSION,
    START_MARKER,
    TEXT_HASH_POLICY,
    file_record,
    logical_path,
    managed_block,
    managed_block_hash,
    safe_relative,
)

LOCAL_METADATA = ".agent-rules-template.json"


def load_json(path: Path) -> dict[str, Any]:
    """읽기 실패·잘못된 JSON을 sync 계약 오류로 보고합니다."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"metadata를 읽을 수 없습니다: {path}") from error
    if not isinstance(value, dict):
        raise ValueError("metadata는 JSON object여야 합니다")
    return value


def inside(root: Path, relative: str) -> Path:
    """번들 참조가 root 밖으로 resolve되면 거부합니다."""
    path = (root / safe_relative(relative)).resolve()
    if path.parent != root.resolve() and root.resolve() not in path.parents:
        raise ValueError(f"프로젝트 밖 경로는 허용되지 않습니다: {relative}")
    return path


def local_target(root: Path, relative: str) -> Path:
    """각 경로 요소의 NFC logical key를 유일한 실제 이름에 대응시킵니다."""
    current = root
    for part in safe_relative(relative).parts:
        if current.exists() and not current.is_dir():
            raise ValueError(f"부모 경로가 directory가 아닙니다: {relative}")
        matches = (
            [p for p in current.iterdir() if logical_path(Path(p.name)) == part]
            if current.is_dir()
            else []
        )
        if len(matches) > 1:
            raise ValueError(f"NFC logical path collision: {relative}")
        current = matches[0] if matches else current / part
        if current.is_symlink() or current.resolve() != current.absolute():
            raise ValueError(f"링크 경로는 허용되지 않습니다: {relative}")
        if root.resolve() not in current.resolve().parents:
            raise ValueError(f"프로젝트 밖 경로: {relative}")
    return current


def validate_baseline(local: dict[str, Any]) -> None:
    """불완전한 baseline을 새 설치로 오인하지 않도록 거부합니다."""
    required = {
        "schema_version",
        "installed_version",
        "hash_policy",
        "managed_block",
        "managed_files",
    }
    if (
        not required <= local.keys()
        or type(local["schema_version"]) is not int
        or local["schema_version"] != SCHEMA_VERSION
    ):
        raise ValueError("불완전하거나 지원하지 않는 local metadata입니다")
    if (
        not isinstance(local["installed_version"], str)
        or not local["installed_version"].strip()
    ):
        raise ValueError("installed version이 없습니다")
    if local["hash_policy"] != {"text": TEXT_HASH_POLICY, "binary": BINARY_HASH_POLICY}:
        raise ValueError("지원하지 않는 local hash policy입니다")
    block = local["managed_block"]
    if not isinstance(block, dict) or not valid_hash(block.get("sha256")):
        raise ValueError("managed block baseline이 손상되었습니다")
    validate_records(local["managed_files"])


def valid_hash(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def validate_records(files: Any) -> None:
    """파일 baseline 형식과 제어 파일·부모 자식 경로 중첩을 검사합니다."""
    if not isinstance(files, dict):
        raise ValueError("managed_files는 object여야 합니다")
    paths = set()
    for raw, record in files.items():
        path = safe_relative(raw)
        if (
            raw in {"AGENTS.md", "metadata.json", LOCAL_METADATA}
            or not isinstance(record, dict)
            or record.get("type") not in {"text", "binary"}
            or not valid_hash(record.get("sha256"))
        ):
            raise ValueError(f"managed file baseline이 손상되었습니다: {raw}")
        paths.add(path)
    if any(parent in paths for path in paths for parent in path.parents):
        raise ValueError("managed file 경로가 중첩됩니다")


def validate_bundle(bundle: Path) -> dict[str, Any]:
    """실제 NFC 파일 집합과 metadata의 버전·hash 계약을 검증합니다."""
    metadata = load_json(bundle / "metadata.json")
    required = {
        "schema_version",
        "template_version",
        "hash_policy",
        "managed_block",
        "managed_files",
    }
    if (
        not required <= metadata.keys()
        or not isinstance(metadata["template_version"], str)
        or not metadata["template_version"]
    ):
        raise ValueError("필수 bundle metadata가 누락되었습니다")
    if (
        type(metadata["schema_version"]) is not int
        or metadata["schema_version"] != SCHEMA_VERSION
        or metadata["hash_policy"]
        != {"text": TEXT_HASH_POLICY, "binary": BINARY_HASH_POLICY}
    ):
        raise ValueError("지원하지 않는 metadata schema 또는 hash policy입니다")
    block = metadata["managed_block"]
    if (
        not isinstance(block, dict)
        or block.get("file") != "AGENTS.md"
        or block.get("start_marker") != START_MARKER
        or block.get("end_marker") != END_MARKER
    ):
        raise ValueError("managed block metadata가 올바르지 않습니다")
    agents = bundle / "AGENTS.md"
    if not agents.is_file() or managed_block_hash(agents) != block.get("sha256"):
        raise ValueError("bundle AGENTS.md hash가 metadata와 다릅니다")
    files = metadata["managed_files"]
    validate_records(files)
    actual = set()
    for path in bundle.rglob("*"):
        relative = path.relative_to(bundle)
        if path.is_symlink() or logical_path(relative) != relative.as_posix():
            raise ValueError(f"NFC가 아니거나 링크인 bundle 경로: {relative}")
        if path.is_file() and relative.as_posix() not in {"AGENTS.md", "metadata.json"}:
            actual.add(relative.as_posix())
    if actual != set(files):
        raise ValueError("실제 bundle 파일 목록과 metadata가 다릅니다")
    if not isinstance(files, dict):
        raise ValueError("managed_files는 object여야 합니다")
    seen: set[str] = set()
    for raw, expected in files.items():
        relative = safe_relative(raw)
        normalized = logical_path(relative)
        if (
            normalized in seen
            or normalized != raw
            or not isinstance(expected, dict)
            or expected.get("type") not in {"text", "binary"}
        ):
            raise ValueError(f"유효하지 않은 managed 경로: {raw}")
        seen.add(normalized)
        source = inside(bundle, raw)
        if not source.is_file() or file_record(source) != expected:
            raise ValueError(f"bundle managed file hash가 다릅니다: {raw}")
    return metadata


def local_modifications(
    project: Path, local: dict[str, Any], replace: bool = False
) -> list[str]:
    """Actual과 baseline을 비교하며 명시적 AGENTS 교체만 비교에서 제외합니다."""
    changes: list[str] = []
    block = local.get("managed_block", {})
    agents = local_target(project, "AGENTS.md")
    if (
        not replace
        and block
        and (not agents.is_file() or managed_block_hash(agents) != block.get("sha256"))
    ):
        changes.append("AGENTS.md managed block")
    for raw, expected in local.get("managed_files", {}).items():
        target = local_target(project, raw)
        if not target.is_file() or file_record(target).get("sha256") != expected.get(
            "sha256"
        ):
            changes.append(raw)
    return changes


def render_agents(template: Path, existing: Path | None, replace: bool) -> str:
    """Project-owned 영역의 줄바꿈을 보존하며 managed block을 갱신합니다."""
    block = managed_block(template.read_text(encoding="utf-8-sig"))
    if existing is None or replace:
        return block + "\n\n# Project Rules\n"
    with existing.open(encoding="utf-8", newline="") as stream:
        current = stream.read()
    if START_MARKER in current or END_MARKER in current:
        return current.replace(managed_block(current), block)
    notice = "<!--\n기존 AGENTS.md의 내용을 보존하여 아래에 이동했습니다.\nTemplate managed rules와 의미가 중복될 수 있으므로 필요하면 LLM으로 정리하십시오.\n-->"
    return block + "\n\n# Project Rules\n\n" + notice + "\n\n" + current


def preflight(
    project: Path,
    bundle: Path,
    metadata: dict[str, Any],
    local: dict[str, Any],
    force: bool,
    replace: bool = False,
) -> None:
    """쓰기 전에 타입·소유권·경로 충돌과 managed 수정 여부를 검사합니다."""
    if local and (
        local.get("schema_version") != SCHEMA_VERSION
        or local.get("hash_policy") != metadata["hash_policy"]
    ):
        raise ValueError("지원하지 않는 local metadata입니다")
    old, new = set(local.get("managed_files", {})), set(metadata["managed_files"])
    targets = [
        local_target(project, raw) for raw in old | new | {"AGENTS.md", LOCAL_METADATA}
    ]
    if len(set(targets)) != len(targets):
        raise ValueError("동일한 실제 대상 경로가 중복됩니다")
    for target in targets:
        if target.exists() and not target.is_file():
            raise ValueError(f"대상 경로가 file이 아닙니다: {target}")
    changes = local_modifications(project, local, replace) if local else []
    if changes and not force:
        raise ValueError(
            "Local modifications detected; no files changed:\n- " + "\n- ".join(changes)
        )
    old, new = set(local.get("managed_files", {})), set(metadata["managed_files"])
    for raw in new:
        target = local_target(project, raw)
        if raw not in old and target.exists():
            raise ValueError(f"Project-owned 파일과 충돌합니다: {raw}")
        parent = target.parent
        while parent != project:
            if parent.exists() and not parent.is_dir():
                raise ValueError(f"부모 경로가 directory가 아닙니다: {raw}")
            parent = parent.parent
    for raw in old - new:
        target = local_target(project, raw)
        if target.exists() and target.is_dir():
            raise ValueError(f"managed file 경로가 directory입니다: {raw}")


def sync(
    project: Path, bundle: Path, force: bool = False, replace: bool = False
) -> None:
    """검증된 bundle을 적용하고 성공한 결과만 새 baseline으로 기록합니다."""
    metadata = validate_bundle(bundle)
    project = project.resolve()
    project.mkdir(parents=True, exist_ok=True)
    local_path = local_target(project, LOCAL_METADATA)
    local = load_json(local_path) if local_path.exists() else {}
    if local_path.exists():
        validate_baseline(local)
    elif local_target(project, "AGENTS.md").is_file():
        current = local_target(project, "AGENTS.md").read_text(encoding="utf-8-sig")
        if START_MARKER in current or END_MARKER in current:
            raise ValueError("기존 managed 설치의 local metadata가 없습니다")
    preflight(project, bundle, metadata, local, force, replace)
    agents = local_target(project, "AGENTS.md")
    if replace and agents.exists():
        print(
            "WARNING:\nAGENTS.md will be replaced.\nExisting Project Rules will be removed.",
            file=sys.stderr,
        )
    rendered = render_agents(
        bundle / "AGENTS.md", agents if agents.exists() else None, replace
    )
    old, new = set(local.get("managed_files", {})), set(metadata["managed_files"])
    writes = {agents: rendered.encode("utf-8")}
    writes.update(
        {local_target(project, raw): inside(bundle, raw).read_bytes() for raw in new}
    )
    deletes = [local_target(project, raw) for raw in old - new]
    baseline = {
        "schema_version": SCHEMA_VERSION,
        "installed_version": metadata["template_version"],
        "hash_policy": metadata["hash_policy"],
        "managed_block": {"sha256": metadata["managed_block"]["sha256"]},
        "managed_files": metadata["managed_files"],
    }
    writes[local_path] = (
        json.dumps(baseline, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")
    apply_changes(project, writes, deletes, metadata)


def apply_changes(
    project: Path,
    writes: dict[Path, bytes],
    deletes: list[Path],
    metadata: dict[str, Any],
) -> None:
    """미리 staging한 파일을 교체하고 예외 발생 시 변경한 대상을 복구합니다."""
    originals = {
        path: path.read_bytes() if path.exists() else None
        for path in [*writes, *deletes]
    }
    changed = []
    created = []
    with tempfile.TemporaryDirectory(
        prefix=".agent-rules-stage-", dir=project
    ) as temporary:
        staging = Path(temporary)
        for index, data in enumerate(writes.values()):
            (staging / str(index)).write_bytes(data)
        try:
            for path in deletes:
                if path.exists():
                    path.unlink()
                    changed.append(path)
            for index, path in enumerate(writes):
                local_target(project, logical_path(path.relative_to(project)))
                missing = []
                parent = path.parent
                while not parent.exists():
                    missing.append(parent)
                    parent = parent.parent
                for directory in reversed(missing):
                    directory.mkdir()
                    created.append(directory)
                # baseline은 결과 검증 이후 마지막으로 교체합니다.
                if path == local_target(project, LOCAL_METADATA):
                    if managed_block_hash(
                        local_target(project, "AGENTS.md")
                    ) != metadata["managed_block"]["sha256"] or any(
                        file_record(local_target(project, raw)) != record
                        for raw, record in metadata["managed_files"].items()
                    ):
                        raise RuntimeError("설치 결과 검증에 실패했습니다")
                os.replace(staging / str(index), path)
                changed.append(path)
        except BaseException:
            for path in reversed(changed):
                if originals[path] is None:
                    path.unlink(missing_ok=True)
                else:
                    backup = staging / "restore"
                    backup.write_bytes(originals[path])
                    os.replace(backup, path)
            for directory in reversed(created):
                directory.rmdir()
            raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument(
        "--bundle", type=Path, default=Path(__file__).resolve().parents[1] / "bundle"
    )
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args(argv)
    try:
        sync(args.project, args.bundle, args.force, args.replace)
    except (OSError, ValueError, RuntimeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Synchronized agent rules into {args.project.resolve()}")
    return 0
