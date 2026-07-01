"""Storage layout versioning and migration."""

from __future__ import annotations

import json
from pathlib import Path

from groundseal.errors import GroundSealError

CURRENT_STORAGE_VERSION = 2
SUPPORTED_VERSIONS = {1, 2}


def read_storage_version(root: Path) -> int:
    meta = root / "_meta" / "version.json"
    if not meta.exists():
        return 1
    data = json.loads(meta.read_text())
    return int(data.get("storage_version", 1))


def write_storage_version(root: Path, version: int = CURRENT_STORAGE_VERSION) -> None:
    meta_dir = root / "_meta"
    meta_dir.mkdir(parents=True, exist_ok=True)
    (meta_dir / "version.json").write_text(
        json.dumps({"storage_version": version}, indent=2) + "\n"
    )


def migrate_storage(root: Path, *, target_version: int = CURRENT_STORAGE_VERSION) -> dict[str, int]:
    """Migrate on-disk layout to target version. Idempotent for v1→v2."""
    root = root.resolve()
    current = read_storage_version(root)

    if current not in SUPPORTED_VERSIONS:
        raise GroundSealError(
            code="STORAGE_MIGRATION_FAILED",
            message="Unsupported storage version",
            details={"current": current},
        )

    if current >= target_version:
        return {"from_version": current, "to_version": current, "files_touched": 0}

    touched = 0
    if current == 1 and target_version >= 2:
        for sub in ("runs", "checkpoints", "patches"):
            (root / sub).mkdir(parents=True, exist_ok=True)
        locks_dir = root / "_meta" / "locks"
        locks_dir.mkdir(parents=True, exist_ok=True)
        write_storage_version(root, target_version)
        touched = 1

    return {"from_version": current, "to_version": target_version, "files_touched": touched}


def ensure_storage_ready(root: Path) -> int:
    """Ensure storage root exists and is at current version."""
    root.mkdir(parents=True, exist_ok=True)
    version = read_storage_version(root)
    if version < CURRENT_STORAGE_VERSION:
        migrate_storage(root, target_version=CURRENT_STORAGE_VERSION)
        version = CURRENT_STORAGE_VERSION
    elif version > CURRENT_STORAGE_VERSION:
        raise GroundSealError(
            code="STORAGE_MIGRATION_FAILED",
            message="Storage version newer than runtime supports",
            details={"current": version, "supported": CURRENT_STORAGE_VERSION},
        )
    return version
