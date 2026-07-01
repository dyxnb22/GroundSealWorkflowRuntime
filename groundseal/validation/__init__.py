"""Input validation beyond schema parsing — fail closed at boundaries."""

from __future__ import annotations

from groundseal.errors import GroundSealError
from groundseal.models import ResumeInput, RunInitialState


def validate_run_initial(initial: RunInitialState) -> None:
    if not initial.workflow_id.strip():
        raise GroundSealError(
            code="INVALID_INITIAL_STATE",
            message="workflow_id must be non-empty",
            details={"workflow_id": initial.workflow_id},
        )
    if initial.run_id is not None and not initial.run_id.strip():
        raise GroundSealError(
            code="INVALID_INITIAL_STATE",
            message="run_id must be non-empty when provided",
            details={},
        )


def validate_resume_input(resume_input: ResumeInput) -> None:
    if not resume_input.run_id.strip():
        raise GroundSealError(
            code="INVALID_RESUME_INPUT",
            message="run_id must be non-empty",
            details={},
        )
    if resume_input.checkpoint_id is not None and not resume_input.checkpoint_id.strip():
        raise GroundSealError(
            code="INVALID_RESUME_INPUT",
            message="checkpoint_id must be non-empty when provided",
            details={},
        )
    if not resume_input.approval.approver_id.strip():
        raise GroundSealError(
            code="INVALID_RESUME_INPUT",
            message="approver_id must be non-empty",
            details={},
        )
