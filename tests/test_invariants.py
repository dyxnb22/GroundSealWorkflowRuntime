"""Invariant enforcement tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from groundseal.errors import GroundSealError
from groundseal.invariants import check_checkpoint_invariants, check_run_state_invariants
from groundseal.models import Checkpoint, CheckpointReason, RunState

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


class TestRunStateInvariants:
    def test_valid_terminal_passes(self) -> None:
        state = RunState.model_validate(_load("run_state/valid_terminal.json"))
        check_run_state_invariants(state)

    def test_valid_running_passes(self) -> None:
        state = RunState.model_validate(_load("run_state/valid_running.json"))
        check_run_state_invariants(state)

    def test_terminal_with_current_node_fails(self) -> None:
        data = _load("run_state/invalid_terminal_mismatch.json")
        state = RunState.model_validate(data)
        with pytest.raises(GroundSealError) as exc:
            check_run_state_invariants(state)
        assert exc.value.code == "INVARIANT_VIOLATION"

    def test_interrupted_without_node_fails(self) -> None:
        data = _load("run_state/valid_running.json")
        data["status"] = "interrupted"
        data["current_node_id"] = None
        state = RunState.model_validate(data)
        with pytest.raises(GroundSealError) as exc:
            check_run_state_invariants(state)
        assert exc.value.code == "INVARIANT_VIOLATION"


class TestCheckpointInvariants:
    def test_valid_checkpoint_passes(self) -> None:
        state = RunState.model_validate(_load("run_state/valid_running.json"))
        cp = Checkpoint(
            checkpoint_id="cp-1",
            run_id=state.run_id,
            state_version=state.state_version,
            state_snapshot=state,
            reason=CheckpointReason.SCHEDULED,
            emitted_at="2026-07-01T00:00:00Z",
        )
        check_checkpoint_invariants(cp)

    def test_run_id_mismatch_fails(self) -> None:
        state = RunState.model_validate(_load("run_state/valid_running.json"))
        cp = Checkpoint(
            checkpoint_id="cp-2",
            run_id="other-run",
            state_version=state.state_version,
            state_snapshot=state,
            reason=CheckpointReason.SCHEDULED,
            emitted_at="2026-07-01T00:00:00Z",
        )
        with pytest.raises(GroundSealError) as exc:
            check_checkpoint_invariants(cp)
        assert exc.value.code == "CHECKPOINT_RUN_MISMATCH"

    def test_version_mismatch_fails(self) -> None:
        state = RunState.model_validate(_load("run_state/valid_running.json"))
        cp = Checkpoint(
            checkpoint_id="cp-3",
            run_id=state.run_id,
            state_version=999,
            state_snapshot=state,
            reason=CheckpointReason.SCHEDULED,
            emitted_at="2026-07-01T00:00:00Z",
        )
        with pytest.raises(GroundSealError) as exc:
            check_checkpoint_invariants(cp)
        assert exc.value.code == "INVARIANT_VIOLATION"
