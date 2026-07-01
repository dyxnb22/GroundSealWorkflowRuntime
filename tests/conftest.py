"""Shared test helpers."""

from __future__ import annotations

from groundseal.models import Approval, ResumeInput, RunInitialState, RunState, RunStatus
from groundseal.runtime import Runtime

CLOCK = "2026-07-01T00:00:00Z"


def run_to_completion(rt: Runtime, initial: RunInitialState) -> RunState:
    """Run fixture workflow through interrupt/resume to completion."""
    first = rt.run(initial)
    if isinstance(first, RunState) and first.status == RunStatus.COMPLETED:
        return first
    from groundseal.models import Interrupt

    assert isinstance(first, Interrupt)
    result = rt.resume(
        ResumeInput(
            run_id=first.run_id,
            checkpoint_id=first.checkpoint_id,
            approval=Approval(approved=True, approver_id="test-reviewer"),
        )
    )
    assert isinstance(result, RunState)
    return result
