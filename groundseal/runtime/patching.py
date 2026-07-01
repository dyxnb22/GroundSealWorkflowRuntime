"""Patch application logic."""

from __future__ import annotations

from groundseal.errors import GroundSealError
from groundseal.invariants import check_run_state_invariants
from groundseal.models import TERMINAL_STATUSES, Patch, RunState
from groundseal.runtime.timeutil import now

ALLOWED_PATCH_PREFIX = "context."


def apply_patch(state: RunState, patch: Patch, *, clock: str | None = None) -> RunState:
    if state.status in TERMINAL_STATUSES:
        raise GroundSealError(
            code="PATCH_ON_TERMINAL",
            message="Cannot apply patch to terminal run",
            details={"status": state.status.value},
        )

    if patch.target_version != state.state_version:
        raise GroundSealError(
            code="VERSION_MISMATCH",
            message="Patch target_version does not match current state",
            details={"expected_version": state.state_version, "target_version": patch.target_version},
        )

    new_state = state.model_copy(deep=True)
    new_context = dict(new_state.context)

    for op in patch.operations:
        if op.op not in ("set", "delete"):
            raise GroundSealError(
                code="INVALID_PATCH",
                message=f"Unsupported operation: {op.op}",
                details={"op": op.op},
            )
        if not op.path.startswith(ALLOWED_PATCH_PREFIX):
            raise GroundSealError(
                code="INVALID_PATCH",
                message=f"Path not allowed: {op.path}",
                details={"path": op.path},
            )
        key = op.path[len(ALLOWED_PATCH_PREFIX) :]
        if not key or key.startswith("_"):
            raise GroundSealError(
                code="INVALID_PATCH",
                message="Cannot patch reserved context keys",
                details={"path": op.path},
            )
        if op.op == "set":
            if op.value is None:
                raise GroundSealError(
                    code="INVALID_PATCH",
                    message="set operation requires value",
                    details={"path": op.path},
                )
            new_context[key] = op.value
        else:
            new_context.pop(key, None)

    new_state.context = new_context
    new_state.state_version += 1
    new_state.updated_at = now(clock)
    check_run_state_invariants(new_state)
    return new_state
