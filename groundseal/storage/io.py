"""Atomic file helpers and ID validation for storage backends."""

from __future__ import annotations

import re
from pathlib import Path

from groundseal.errors import GroundSealError

_SAFE_ID = re.compile(r"^[A-Za-z0-9._-]+$")


def validate_storage_id(value: str, *, field: str) -> str:
    if not value or not _SAFE_ID.match(value):
        raise GroundSealError(
            code="INVALID_STORAGE_ID",
            message=f"Invalid {field} for storage path",
            details={"field": field, "value": value},
        )
    return value


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content)
    tmp.replace(path)
