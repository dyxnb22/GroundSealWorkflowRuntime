"""Checkpoint emission."""

from __future__ import annotations

import uuid

from groundseal.invariants import check_checkpoint_invariants, check_run_state_invariants
from groundseal.models import Checkpoint, CheckpointReason, RunState
from groundseal.runtime.timeutil import now


def emit_checkpoint(
    state: RunState,
    *,
    reason: CheckpointReason = CheckpointReason.SCHEDULED,
    clock: str | None = None,
    checkpoint_id: str | None = None,
) -> Checkpoint:
    check_run_state_invariants(state)
    checkpoint = Checkpoint(
        checkpoint_id=checkpoint_id or str(uuid.uuid4()),
        run_id=state.run_id,
        state_version=state.state_version,
        state_snapshot=state.model_copy(deep=True),
        reason=reason,
        emitted_at=now(clock),
    )
    check_checkpoint_invariants(checkpoint)
    return checkpoint
