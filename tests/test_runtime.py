"""Runtime and end-to-end scenario tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from groundseal.errors import GroundSealError
from groundseal.models import (
    Approval,
    ApprovalDenialPolicy,
    Interrupt,
    Patch,
    ResumeInput,
    RunInitialState,
    RunState,
    RunStatus,
)
from groundseal.runtime import InMemoryRuntime, Runtime, apply_patch, branch_select
from tests.conftest import CLOCK, run_to_completion

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


class TestHappyPathRunComplete:
    def test_run_completes_via_interrupt_and_resume(self) -> None:
        rt = InMemoryRuntime(clock=CLOCK)
        initial = RunInitialState.model_validate(_load("happy_path_run_complete/valid.json"))
        result = run_to_completion(rt, initial)
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

    def test_reserved_context_key_rejected(self) -> None:
        rt = InMemoryRuntime(clock=CLOCK)
        initial = RunInitialState(
            workflow_id="fixture_approval_v1",
            context={"_approval_granted": True},
        )
        with pytest.raises(GroundSealError) as exc:
            rt.run(initial)
        assert exc.value.code == "INVALID_INITIAL_STATE"


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

    def test_resume_without_explicit_checkpoint_id(self) -> None:
        rt = InMemoryRuntime(clock=CLOCK)
        initial = RunInitialState.model_validate(_load("interrupt_at_approval_then_resume/valid.json"))
        interrupt = rt.run(initial)
        assert isinstance(interrupt, Interrupt)
        resumed = rt.resume(
            ResumeInput(
                run_id=interrupt.run_id,
                approval=Approval(approved=True, approver_id="reviewer-1"),
            )
        )
        assert isinstance(resumed, RunState)
        assert resumed.status == RunStatus.COMPLETED

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

    def test_remain_interrupted_policy_allows_retry(self) -> None:
        rt = Runtime(
            clock=CLOCK,
            denial_policy=ApprovalDenialPolicy.REMAIN_INTERRUPTED,
        )
        initial = RunInitialState(
            workflow_id="fixture_approval_v1",
            run_id="remain-interrupted-001",
            context={},
        )
        interrupt = rt.run(initial)
        assert isinstance(interrupt, Interrupt)

        with pytest.raises(GroundSealError) as exc:
            rt.resume(
                ResumeInput(
                    run_id=interrupt.run_id,
                    checkpoint_id=interrupt.checkpoint_id,
                    approval=Approval(approved=False, approver_id="denier"),
                )
            )
        assert exc.value.code == "APPROVAL_DENIED"
        assert rt.get_run(interrupt.run_id).status == RunStatus.INTERRUPTED

        approved = rt.resume(
            ResumeInput(
                run_id=interrupt.run_id,
                approval=Approval(approved=True, approver_id="approver"),
            )
        )
        assert isinstance(approved, RunState)
        assert approved.status == RunStatus.COMPLETED


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

    def test_reserved_context_patch_rejected(self) -> None:
        state = RunState.model_validate(_load("run_state/valid_running.json"))
        patch = Patch(
            patch_id="patch-reserved",
            target_version=0,
            operations=[{"op": "set", "path": "context._approval_granted", "value": True}],
        )
        with pytest.raises(GroundSealError) as exc:
            apply_patch(state, patch, clock=CLOCK)
        assert exc.value.code == "INVALID_PATCH"


class TestStaleCheckpoint:
    def test_stale_checkpoint_on_resume_rejected(self) -> None:
        rt = InMemoryRuntime(clock=CLOCK)
        initial = RunInitialState.model_validate(_load("interrupt_at_approval_then_resume/valid.json"))
        interrupt = rt.run(initial)
        assert isinstance(interrupt, Interrupt)

        state = rt.get_run(interrupt.run_id)
        bumped = state.model_copy(deep=True)
        bumped.state_version += 5
        rt.persist_run(bumped)

        with pytest.raises(GroundSealError) as exc:
            rt.resume(
                ResumeInput(
                    run_id=interrupt.run_id,
                    checkpoint_id=interrupt.checkpoint_id,
                    approval=Approval(approved=True, approver_id="reviewer-3"),
                )
            )
        assert exc.value.code == "STALE_CHECKPOINT"

    def test_checkpoint_run_mismatch_on_resume(self) -> None:
        rt = InMemoryRuntime(clock=CLOCK)
        run_a = RunInitialState(workflow_id="fixture_approval_v1", run_id="run-a-001", context={})
        run_b = RunInitialState(workflow_id="fixture_approval_v1", run_id="run-b-001", context={})
        interrupt_a = rt.run(run_a)
        rt.run(run_b)
        assert isinstance(interrupt_a, Interrupt)

        with pytest.raises(GroundSealError) as exc:
            rt.resume(
                ResumeInput(
                    run_id="run-b-001",
                    checkpoint_id=interrupt_a.checkpoint_id,
                    approval=Approval(approved=True, approver_id="reviewer"),
                )
            )
        assert exc.value.code == "CHECKPOINT_RUN_MISMATCH"

    def test_unknown_node_on_resume(self) -> None:
        rt = InMemoryRuntime(clock=CLOCK)
        initial = RunInitialState(
            workflow_id="fixture_approval_v1",
            run_id="bad-node-001",
            context={},
        )
        interrupt = rt.run(initial)
        assert isinstance(interrupt, Interrupt)

        cp = rt.list_checkpoints(interrupt.run_id)[0]
        corrupted_cp = cp.model_copy(deep=True)
        corrupted_cp.state_snapshot = corrupted_cp.state_snapshot.model_copy(deep=True)
        corrupted_cp.state_snapshot.current_node_id = "nonexistent_node"
        rt._storage.save_checkpoint(corrupted_cp)

        corrupted_run = rt.get_run(interrupt.run_id)
        corrupted_run = corrupted_run.model_copy(deep=True)
        corrupted_run.current_node_id = "nonexistent_node"
        rt.persist_run(corrupted_run)

        with pytest.raises(GroundSealError) as exc:
            rt.resume(
                ResumeInput(
                    run_id=interrupt.run_id,
                    checkpoint_id=interrupt.checkpoint_id,
                    approval=Approval(approved=True, approver_id="reviewer"),
                )
            )
        assert exc.value.code == "NODE_NOT_FOUND"


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
        loaded = rt.list_checkpoints(state.run_id)
        assert any(c.checkpoint_id == cp.checkpoint_id for c in loaded)

    def test_deterministic_repeat_runs(self) -> None:
        results = []
        for _ in range(3):
            rt = InMemoryRuntime(clock=CLOCK)
            initial = RunInitialState.model_validate(_load("happy_path_run_complete/valid.json"))
            result = run_to_completion(rt, initial)
            results.append(result.status)
        assert results == [RunStatus.COMPLETED] * 3
