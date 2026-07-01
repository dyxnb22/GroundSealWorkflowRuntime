"""File storage and multi-session restart tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from groundseal.errors import GroundSealError
from groundseal.models import Approval, Patch, ResumeInput, RunInitialState, RunState, RunStatus
from groundseal.runtime import Runtime
from groundseal.storage import FileStorage

CLOCK = "2026-07-01T00:00:00Z"


@pytest.fixture
def storage_dir(tmp_path: Path) -> Path:
    return tmp_path / "groundseal_data"


class TestFileStorage:
    def test_interrupt_survives_runtime_restart(self, storage_dir: Path) -> None:
        run_id = "persist-run-001"
        initial = RunInitialState(
            workflow_id="fixture_approval_v1",
            run_id=run_id,
            context={"branch_key": "a"},
        )

        rt1 = Runtime(storage=FileStorage(storage_dir), clock=CLOCK)
        interrupt = rt1.run(initial)
        assert hasattr(interrupt, "checkpoint_id")

        rt2 = Runtime(storage=FileStorage(storage_dir), clock=CLOCK)
        state = rt2.get_run(run_id)
        assert state.status == RunStatus.INTERRUPTED

        final = rt2.resume(
            ResumeInput(
                run_id=run_id,
                checkpoint_id=interrupt.checkpoint_id,
                approval=Approval(approved=True, approver_id="persist-reviewer"),
            )
        )
        assert final.status == RunStatus.COMPLETED

    def test_checkpoint_persisted_to_disk(self, storage_dir: Path) -> None:
        rt = Runtime(storage=FileStorage(storage_dir), clock=CLOCK)
        initial = RunInitialState(
            workflow_id="fixture_approval_v1",
            run_id="persist-run-002",
            context={},
        )
        interrupt = rt.run(initial)
        cp_path = storage_dir / "checkpoints" / f"{interrupt.checkpoint_id}.json"
        assert cp_path.exists()

    def test_patch_tracking_persists(self, storage_dir: Path) -> None:
        storage = FileStorage(storage_dir)
        rt = Runtime(storage=storage, clock=CLOCK)
        state = RunState(
            run_id="persist-patch-001",
            state_version=0,
            status=RunStatus.RUNNING,
            current_node_id="node_prepare",
            created_at=CLOCK,
            updated_at=CLOCK,
        )
        storage.save_run(state)
        patch = Patch(
            patch_id="persist-patch-id-001",
            target_version=0,
            operations=[{"op": "set", "path": "context.k", "value": "v"}],
        )
        rt.apply_patch(state, patch)

        rt2 = Runtime(storage=FileStorage(storage_dir), clock=CLOCK)
        updated = rt2.get_run("persist-patch-001")
        assert updated.context["k"] == "v"
        with pytest.raises(GroundSealError) as exc:
            rt2.apply_patch(updated, patch)
        assert exc.value.code == "DUPLICATE_PATCH"

    def test_corrupt_run_file_raises(self, storage_dir: Path) -> None:
        storage = FileStorage(storage_dir)
        run_id = "corrupt-run-001"
        path = storage_dir / "runs" / f"{run_id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{not valid json")
        with pytest.raises(GroundSealError) as exc:
            storage.load_run(run_id)
        assert exc.value.code == "STORAGE_CORRUPT"
