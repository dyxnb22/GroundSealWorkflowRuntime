"""Runtime and end-to-end scenario tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from groundseal.errors import GroundSealError
from groundseal.models import Approval, Interrupt, ResumeInput, RunInitialState, RunState, RunStatus
from groundseal.runtime import InMemoryRuntime, apply_patch, branch_select
from groundseal.models import Patch

FIXTURES = Path(__file__).parent / "fixtures"
CLOCK = "2026-07-01T00:00:00Z"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


class TestHappyPathRunComplete:
    def test_run_completes_without_interrupt(self) -> None:
        rt = InMemoryRuntime(clock=CLOCK)
        initial = RunInitialState.model_validate(_load("happy_path_run_complete/valid.json"))
        result = rt.run(initial)
        assert isinstance(result, RunState)
        assert result.status == RunStatus.COMPLETED
        assert result.current_node_id is None
        assert "node_prepare" in result.node_results
        assert "node_execute" in result.node_results

    def test_unknown_workflow_rejected(self) -> None:
        rt = InMemoryRuntime(clock=CLOCK)
        initial = RunInitialState.model_validate(_load("happy_path_run_complete/invalid.json"))
        with pytest.raises(GroundSealError) as exc:
            rt.run(initial)
        assert exc.value.code == "WORKFLOW_NOT_FOUND"


class TestInterruptAndResume:
    def test_interrupt_then_resume_completes(self) -> None:
        rt = InMemoryRuntime(clock=CLOCK)
        initial = RunInitialState.model_validate(_load("interrupt_at_approval_then_resume/valid.json"))
        first = rt.run(initial)
        assert isinstance(first, Interrupt)
        assert first.reason == "approval_required"
        assert first.node_id == "node_execute"

        resumed = rt.resume(
            ResumeInput(
                run_id=first.run_id,
                checkpoint_id=first.checkpoint_id,
                approval=Approval(approved=True, approver_id="reviewer-1"),
            )
        )
        assert isinstance(resumed, RunState)
        assert resumed.status == RunStatus.COMPLETED
        assert resumed.context.get("_approval_granted") is True

    def test_denied_approval_fails_run(self) -> None:
        rt = InMemoryRuntime(clock=CLOCK)
        initial = RunInitialState.model_validate(_load("interrupt_at_approval_then_resume/valid.json"))
        interrupt = rt.run(initial)
        assert isinstance(interrupt, Interrupt)

        with pytest.raises(GroundSealError) as exc:
            rt.resume(
                ResumeInput(
                    run_id=interrupt.run_id,
                    checkpoint_id=interrupt.checkpoint_id,
                    approval=Approval(approved=False, approver_id="reviewer-2"),
                )
            )
        assert exc.value.code == "APPROVAL_DENIED"
        state = rt.get_run(interrupt.run_id)
        assert state.status == RunStatus.FAILED


class TestInvalidPatchRejected:
    def test_version_mismatch_rejected(self) -> None:
        data = _load("invalid_patch_rejected/invalid.json")
        state = RunState.model_validate({k: v for k, v in data.items() if k != "patch"})
        patch = Patch.model_validate(data["patch"])
        with pytest.raises(GroundSealError) as exc:
            apply_patch(state, patch, clock=CLOCK)
        assert exc.value.code == "VERSION_MISMATCH"

    def test_valid_patch_applied(self) -> None:
        data = _load("invalid_patch_rejected/valid.json")
        state = RunState.model_validate({k: v for k, v in data.items() if k != "patch"})
        patch = Patch.model_validate(data["patch"])
        updated = apply_patch(state, patch, clock=CLOCK)
        assert updated.state_version == 2
        assert updated.context["approval_token"] == "ok"

    def test_patch_on_terminal_rejected(self) -> None:
        state = RunState.model_validate(_load("run_state/valid_terminal.json"))
        patch = Patch.model_validate(_load("invalid_patch_rejected/valid.json")["patch"])
        with pytest.raises(GroundSealError) as exc:
            apply_patch(state, patch, clock=CLOCK)
        assert exc.value.code == "PATCH_ON_TERMINAL"

    def test_disallowed_path_rejected(self) -> None:
        data = _load("run_state/valid_running.json")
        state = RunState.model_validate(data)
        patch = Patch.model_validate(_load("invalid_patch_rejected/invalid_path.json"))
        with pytest.raises(GroundSealError) as exc:
            apply_patch(state, patch, clock=CLOCK)
        assert exc.value.code == "INVALID_PATCH"


class TestStaleCheckpoint:
    def test_stale_checkpoint_on_resume_rejected(self) -> None:
        rt = InMemoryRuntime(clock=CLOCK)
        initial = RunInitialState.model_validate(_load("interrupt_at_approval_then_resume/valid.json"))
        interrupt = rt.run(initial)
        assert isinstance(interrupt, Interrupt)

        # Advance state version artificially without matching checkpoint
        state = rt.get_run(interrupt.run_id)
        bumped = state.model_copy(deep=True)
        bumped.state_version += 5
        rt._storage.save_run(bumped)  # test-only: simulate drift

        with pytest.raises(GroundSealError) as exc:
            rt.resume(
                ResumeInput(
                    run_id=interrupt.run_id,
                    checkpoint_id=interrupt.checkpoint_id,
                    approval=Approval(approved=True, approver_id="reviewer-3"),
                )
            )
        assert exc.value.code == "STALE_CHECKPOINT"


class TestBranchDeterminism:
    def test_same_input_same_edge(self) -> None:
        ctx = _load("branch_determinism_same_input/valid.json")["context"]
        a = branch_select(ctx)
        b = branch_select(ctx)
        assert a.selected_edge == b.selected_edge
        assert a.inputs_hash == b.inputs_hash
        assert a.decision_id == b.decision_id

    def test_different_key_different_edge(self) -> None:
        ctx_a = _load("branch_determinism_same_input/valid.json")["context"]
        ctx_b = _load("branch_determinism_same_input/invalid.json")["context"]
        ctx_b["branch_key"] = "b"
        assert branch_select(ctx_a).selected_edge != branch_select(ctx_b).selected_edge


class TestEmitCheckpoint:
    def test_emit_checkpoint_stores_snapshot(self) -> None:
        rt = InMemoryRuntime(clock=CLOCK)
        state = RunState.model_validate(_load("run_state/valid_running.json"))
        cp = rt.emit_checkpoint(state)
        loaded = rt._storage.load_checkpoint(cp.checkpoint_id)
        assert loaded is not None
        assert loaded.state_snapshot.state_version == state.state_version

    def test_deterministic_repeat_runs(self) -> None:
        """Same fixture run three times yields consistent structure."""
        results = []
        for _ in range(3):
            rt = InMemoryRuntime(clock=CLOCK)
            initial = RunInitialState.model_validate(_load("happy_path_run_complete/valid.json"))
            result = rt.run(initial)
            assert isinstance(result, RunState)
            results.append(result.status)
        assert results == [RunStatus.COMPLETED] * 3
