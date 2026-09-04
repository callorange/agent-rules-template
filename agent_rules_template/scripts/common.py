"""번들 metadata와 hash 정책을 build·sync가 함께 사용합니다."""

from __future__ import annotations

import hashlib
import json
import unicodedata
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
TEXT_HASH_POLICY = "text-v1"
BINARY_HASH_POLICY = "binary-v1"
START_MARKER = "<!-- agent-rules-template:managed:start -->"
END_MARKER = "<!-- agent-rules-template:managed:end -->"


def logical_path(path: Path) -> str:
    return unicodedata.normalize("NFC", path.as_posix())


def safe_relative(raw: str) -> Path:
    """OS와 무관하게 NFC 상대 파일 경로만 허용합니다."""
    if not isinstance(raw, str) or "\\" in raw or ":" in raw:
        raise ValueError(f"허용되지 않는 managed 경로: {raw}")
    path = Path(raw)
    if (
        not raw
        or path.is_absolute()
        or any(part in {"", ".", ".."} for part in raw.split("/"))
    ):
        raise ValueError(f"허용되지 않는 managed 경로: {raw}")
    if logical_path(path) != raw:
        raise ValueError(f"NFC 정규화되지 않은 managed 경로: {raw}")
    return path


def canonical_text_bytes(data: bytes) -> bytes:
    text = data.decode("utf-8-sig")
    text = unicodedata.normalize("NFC", text).replace("\r\n", "\n").replace("\r", "\n")
    return text.rstrip("\n").encode("utf-8") + b"\n"


def sha256_bytes(data: bytes, file_type: str) -> str:
    return hashlib.sha256(
        canonical_text_bytes(data) if file_type == "text" else data
    ).hexdigest()


def is_text_file(path: Path) -> bool:
    data = path.read_bytes()
    if b"\0" in data:
        return False
    try:
        data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return False
    return True


def file_record(path: Path) -> dict[str, str]:
    kind = "text" if is_text_file(path) else "binary"
    return {"type": kind, "sha256": sha256_bytes(path.read_bytes(), kind)}


def managed_block(text: str) -> str:
    if text.count(START_MARKER) != 1 or text.count(END_MARKER) != 1:
        raise ValueError("AGENTS.md marker가 정확히 하나씩 있어야 합니다")
    start, end = text.index(START_MARKER), text.index(END_MARKER)
    if end < start:
        raise ValueError("AGENTS.md marker 순서가 올바르지 않습니다")
    return text[start : end + len(END_MARKER)]


def managed_block_hash(path: Path) -> str:
    return sha256_bytes(
        managed_block(path.read_text(encoding="utf-8-sig")).encode(), "text"
    )


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
