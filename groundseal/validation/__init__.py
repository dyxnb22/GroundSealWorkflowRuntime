"""Input validation beyond schema parsing — fail closed at boundaries."""

from __future__ import annotations

from typing import Any

from groundseal.constants import INTERNAL_CONTEXT_KEYS, INTERNAL_CONTEXT_PREFIX
from groundseal.errors import GroundSealError
from groundseal.models import ResumeInput, RunInitialState


def _find_reserved_context_keys(context: dict[str, Any]) -> list[str]:
    reserved: list[str] = []
    for key in context:
        if key in INTERNAL_CONTEXT_KEYS or key.startswith(INTERNAL_CONTEXT_PREFIX):
            reserved.append(key)
    return reserved


def sanitize_caller_context(context: dict[str, Any]) -> dict[str, Any]:
    """Return caller context with runtime-internal keys removed."""
    return {k: v for k, v in context.items() if k not in INTERNAL_CONTEXT_KEYS and not k.startswith(INTERNAL_CONTEXT_PREFIX)}


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
    reserved = _find_reserved_context_keys(initial.context)
    if reserved:
        raise GroundSealError(
            code="INVALID_INITIAL_STATE",
            message="Context contains reserved runtime-internal keys",
            details={"reserved_keys": reserved},
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
