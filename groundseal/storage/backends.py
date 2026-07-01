"""Run and checkpoint persistence backends."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from groundseal.models import Checkpoint, RunState


class StorageBackend(Protocol):
    def save_run(self, state: RunState) -> None: ...
    def load_run(self, run_id: str) -> RunState | None: ...
    def save_checkpoint(self, checkpoint: Checkpoint) -> None: ...
    def load_checkpoint(self, checkpoint_id: str) -> Checkpoint | None: ...
    def list_checkpoint_ids(self, run_id: str) -> list[str]: ...
    def has_applied_patch(self, run_id: str, patch_id: str) -> bool: ...
    def mark_patch_applied(self, run_id: str, patch_id: str) -> None: ...


class MemoryStorage:
    """In-process storage (Phase 2 default)."""

    def __init__(self) -> None:
        self._runs: dict[str, RunState] = {}
        self._checkpoints: dict[str, Checkpoint] = {}
        self._checkpoints_by_run: dict[str, list[str]] = {}
        self._applied_patches: dict[str, set[str]] = {}

    def save_run(self, state: RunState) -> None:
        self._runs[state.run_id] = state.model_copy(deep=True)

    def load_run(self, run_id: str) -> RunState | None:
        state = self._runs.get(run_id)
        return state.model_copy(deep=True) if state else None

    def save_checkpoint(self, checkpoint: Checkpoint) -> None:
        self._checkpoints[checkpoint.checkpoint_id] = checkpoint.model_copy(deep=True)
        ids = self._checkpoints_by_run.setdefault(checkpoint.run_id, [])
        if checkpoint.checkpoint_id not in ids:
            ids.append(checkpoint.checkpoint_id)

    def load_checkpoint(self, checkpoint_id: str) -> Checkpoint | None:
        cp = self._checkpoints.get(checkpoint_id)
        return cp.model_copy(deep=True) if cp else None

    def list_checkpoint_ids(self, run_id: str) -> list[str]:
        return list(self._checkpoints_by_run.get(run_id, []))

    def has_applied_patch(self, run_id: str, patch_id: str) -> bool:
        return patch_id in self._applied_patches.get(run_id, set())

    def mark_patch_applied(self, run_id: str, patch_id: str) -> None:
        self._applied_patches.setdefault(run_id, set()).add(patch_id)


class FileStorage:
    """JSON file persistence for durable multi-session runs (Phase 6)."""

    def __init__(self, root: Path | str) -> None:
        self._root = Path(root)
        self._runs_dir = self._root / "runs"
        self._checkpoints_dir = self._root / "checkpoints"
        self._patches_dir = self._root / "patches"
        for d in (self._runs_dir, self._checkpoints_dir, self._patches_dir):
            d.mkdir(parents=True, exist_ok=True)

    def _run_path(self, run_id: str) -> Path:
        return self._runs_dir / f"{run_id}.json"

    def _checkpoint_path(self, checkpoint_id: str) -> Path:
        return self._checkpoints_dir / f"{checkpoint_id}.json"

    def _patches_path(self, run_id: str) -> Path:
        return self._patches_dir / f"{run_id}.json"

    def save_run(self, state: RunState) -> None:
        self._run_path(state.run_id).write_text(state.model_dump_json(indent=2) + "\n")

    def load_run(self, run_id: str) -> RunState | None:
        path = self._run_path(run_id)
        if not path.exists():
            return None
        return RunState.model_validate_json(path.read_text())

    def save_checkpoint(self, checkpoint: Checkpoint) -> None:
        self._checkpoint_path(checkpoint.checkpoint_id).write_text(
            checkpoint.model_dump_json(indent=2) + "\n"
        )
        index_path = self._checkpoints_dir / f"_index_{checkpoint.run_id}.json"
        ids: list[str] = []
        if index_path.exists():
            ids = json.loads(index_path.read_text())
        if checkpoint.checkpoint_id not in ids:
            ids.append(checkpoint.checkpoint_id)
            index_path.write_text(json.dumps(ids, indent=2) + "\n")

    def load_checkpoint(self, checkpoint_id: str) -> Checkpoint | None:
        path = self._checkpoint_path(checkpoint_id)
        if not path.exists():
            return None
        return Checkpoint.model_validate_json(path.read_text())

    def list_checkpoint_ids(self, run_id: str) -> list[str]:
        index_path = self._checkpoints_dir / f"_index_{run_id}.json"
        if not index_path.exists():
            return []
        return json.loads(index_path.read_text())

    def has_applied_patch(self, run_id: str, patch_id: str) -> bool:
        path = self._patches_path(run_id)
        if not path.exists():
            return False
        return patch_id in json.loads(path.read_text())

    def mark_patch_applied(self, run_id: str, patch_id: str) -> None:
        path = self._patches_path(run_id)
        ids: list[str] = json.loads(path.read_text()) if path.exists() else []
        if patch_id not in ids:
            ids.append(patch_id)
            path.write_text(json.dumps(ids, indent=2) + "\n")
