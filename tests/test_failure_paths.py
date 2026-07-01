"""Phase 3 negative-path and adversarial regression tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from groundseal.errors import GroundSealError
from groundseal.models import Approval, Patch, PatchOperation, ResumeInput, RunInitialState, RunState, RunStatus
from groundseal.runtime import InMemoryRuntime, apply_patch
from groundseal.validation import validate_resume_input, validate_run_initial

FIXTURES = Path(__file__).parent / "fixtures" / "failures"
CLOCK = "2026-07-01T00:00:00Z"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


class TestMalformedResume:
    def test_empty_approver_id_rejected(self) -> None:
        resume = ResumeInput(
            run_id="run-1",
            approval=Approval(approved=True, approver_id=""),
        )
        with pytest.raises(GroundSealError) as exc:
            validate_resume_input(resume)
        assert exc.value.code == "INVALID_RESUME_INPUT"

    def test_empty_run_id_rejected(self) -> None:
        resume = ResumeInput(
            run_id="  ",
            approval=Approval(approved=True, approver_id="reviewer"),
        )
        with pytest.raises(GroundSealError) as exc:
            validate_resume_input(resume)
        assert exc.value.code == "INVALID_RESUME_INPUT"

    def test_resume_unknown_run(self) -> None:
        rt = InMemoryRuntime(clock=CLOCK)
        with pytest.raises(GroundSealError) as exc:
            rt.resume(
                ResumeInput(
                    run_id="00000000-0000-0000-0000-000000000099",
                    approval=Approval(approved=True, approver_id="reviewer"),
                )
            )
        assert exc.value.code == "RUN_NOT_FOUND"

    def test_resume_completed_run_rejected(self) -> None:
        rt = InMemoryRuntime(clock=CLOCK)
        initial = RunInitialState(
            workflow_id="fixture_approval_v1",
            run_id="fail-resume-terminal-001",
            context={},
        )
        from tests.conftest import run_to_completion

        run_to_completion(rt, initial)
        with pytest.raises(GroundSealError) as exc:
            rt.resume(
                ResumeInput(
                    run_id="fail-resume-terminal-001",
                    approval=Approval(approved=True, approver_id="reviewer"),
                )
            )
        assert exc.value.code in ("RUN_NOT_INTERRUPTED", "RUN_TERMINAL")


class TestAdversarialPatch:
    def test_unsupported_op_rejected(self) -> None:
        state = RunState.model_validate(_load("running_state.json"))
        patch = Patch(
            patch_id="fail-patch-001",
            target_version=1,
            operations=[PatchOperation.model_construct(op="replace", path="context.x", value=1)],
        )
        with pytest.raises(GroundSealError) as exc:
            from groundseal.runtime import apply_patch

            apply_patch(state, patch, clock=CLOCK)
        assert exc.value.code == "INVALID_PATCH"

    def test_set_without_value_rejected(self) -> None:
        state = RunState.model_validate(_load("running_state.json"))
        patch = Patch.model_validate(_load("patch_set_no_value.json"))
        with pytest.raises(GroundSealError) as exc:
            apply_patch(state, patch, clock=CLOCK)
        assert exc.value.code == "INVALID_PATCH"

    def test_duplicate_patch_rejected(self) -> None:
        rt = InMemoryRuntime(clock=CLOCK)
        state = RunState.model_validate(_load("running_state.json"))
        patch = Patch.model_validate(_load("patch_valid_context.json"))
        rt.apply_patch(state, patch)
        with pytest.raises(GroundSealError) as exc:
            rt.apply_patch(rt.get_run(state.run_id), patch)
        assert exc.value.code == "DUPLICATE_PATCH"


class TestMalformedRunInitial:
    def test_empty_workflow_id_rejected(self) -> None:
        initial = RunInitialState(workflow_id="  ", context={})
        with pytest.raises(GroundSealError) as exc:
            validate_run_initial(initial)
        assert exc.value.code == "INVALID_INITIAL_STATE"

    def test_empty_run_id_rejected(self) -> None:
        initial = RunInitialState(workflow_id="fixture_approval_v1", run_id="  ")
        with pytest.raises(GroundSealError) as exc:
            validate_run_initial(initial)
        assert exc.value.code == "INVALID_INITIAL_STATE"

    def test_reserved_context_key_rejected(self) -> None:
        initial = RunInitialState(
            workflow_id="fixture_approval_v1",
            context={"_approval_granted": True},
        )
        with pytest.raises(GroundSealError) as exc:
            validate_run_initial(initial)
        assert exc.value.code == "INVALID_INITIAL_STATE"


class TestCheckpointMismatch:
    def test_wrong_checkpoint_run_id_on_resume(self) -> None:
        rt = InMemoryRuntime(clock=CLOCK)
        initial = RunInitialState(
            workflow_id="fixture_approval_v1",
            run_id="fail-cp-mismatch-001",
            context={},
        )
        interrupt = rt.run(initial)
        assert hasattr(interrupt, "checkpoint_id")
        with pytest.raises(GroundSealError) as exc:
            rt.resume(
                ResumeInput(
                    run_id="fail-cp-mismatch-001",
                    checkpoint_id="00000000-0000-0000-0000-000000000099",
                    approval=Approval(approved=True, approver_id="reviewer"),
                )
            )
        assert exc.value.code == "CHECKPOINT_NOT_FOUND"
