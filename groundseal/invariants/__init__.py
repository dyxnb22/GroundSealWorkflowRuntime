"""Invariant checks — rules that must always hold."""

from __future__ import annotations

from groundseal.errors import GroundSealError
from groundseal.models import TERMINAL_STATUSES, Checkpoint, RunState, RunStatus


def check_run_state_invariants(state: RunState) -> None:
    """Validate RunState invariants; raise GroundSealError on violation."""
    if state.status in TERMINAL_STATUSES and state.current_node_id is not None:
        raise GroundSealError(
            code="INVARIANT_VIOLATION",
            message="Terminal run must not have a current_node_id",
            details={"status": state.status.value, "current_node_id": state.current_node_id},
        )

    if state.status == RunStatus.INTERRUPTED and state.current_node_id is None:
        raise GroundSealError(
            code="INVARIANT_VIOLATION",
            message="Interrupted run must record the interrupted node",
            details={"status": state.status.value},
        )

    for node_id, result in state.node_results.items():
        if result.node_id != node_id:
            raise GroundSealError(
                code="INVARIANT_VIOLATION",
                message="node_results key must match NodeResult.node_id",
                details={"key": node_id, "node_id": result.node_id},
            )


def check_checkpoint_invariants(checkpoint: Checkpoint) -> None:
    """Validate checkpoint consistency with its embedded snapshot."""
    if checkpoint.run_id != checkpoint.state_snapshot.run_id:
        raise GroundSealError(
            code="CHECKPOINT_RUN_MISMATCH",
            message="Checkpoint run_id must match state snapshot",
            details={"checkpoint_run_id": checkpoint.run_id, "snapshot_run_id": checkpoint.state_snapshot.run_id},
        )

    if checkpoint.state_version != checkpoint.state_snapshot.state_version:
        raise GroundSealError(
            code="INVARIANT_VIOLATION",
            message="Checkpoint state_version must match snapshot",
            details={
                "checkpoint": checkpoint.state_version,
                "snapshot": checkpoint.state_snapshot.state_version,
            },
        )

    check_run_state_invariants(checkpoint.state_snapshot)
