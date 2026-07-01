"""Public API: run, resume, apply_patch, emit_checkpoint."""

from __future__ import annotations

import hashlib
import json
import uuid
from typing import Any

from groundseal.errors import GroundSealError
from groundseal.invariants import check_checkpoint_invariants, check_run_state_invariants
from groundseal.models import (
    TERMINAL_STATUSES,
    BranchDecision,
    Checkpoint,
    CheckpointReason,
    Interrupt,
    NodeDefinition,
    NodeResult,
    Patch,
    ResumeInput,
    RunInitialState,
    RunState,
    RunStatus,
)
from groundseal.storage import MemoryStorage, StorageBackend
from groundseal.validation import validate_resume_input, validate_run_initial

FIXTURE_WORKFLOW_ID = "fixture_approval_v1"

FIXTURE_NODES: list[NodeDefinition] = [
    NodeDefinition(node_id="node_prepare", requires_approval=False, handler="prepare"),
    NodeDefinition(node_id="node_execute", requires_approval=True, handler="execute"),
]

ALLOWED_PATCH_PREFIX = "context."


def _now(clock: str | None) -> str:
    return clock or "2026-07-01T00:00:00Z"


def branch_select(context: dict[str, Any]) -> BranchDecision:
    """Deterministic branch from context inputs."""
    payload = json.dumps(context, sort_keys=True)
    inputs_hash = hashlib.sha256(payload.encode()).hexdigest()
    selected_edge = "edge_a" if context.get("branch_key", "a") == "a" else "edge_b"
    return BranchDecision(
        decision_id=str(uuid.uuid5(uuid.NAMESPACE_DNS, inputs_hash)),
        inputs_hash=inputs_hash,
        selected_edge=selected_edge,
    )


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
        if not key:
            raise GroundSealError(
                code="INVALID_PATCH",
                message="Empty context key path",
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
    new_state.updated_at = _now(clock)
    check_run_state_invariants(new_state)
    return new_state


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
        emitted_at=_now(clock),
    )
    check_checkpoint_invariants(checkpoint)
    return checkpoint


class Runtime:
    """Workflow runtime with pluggable storage backend."""

    def __init__(self, *, storage: StorageBackend | None = None, clock: str | None = None) -> None:
        self._storage = storage or MemoryStorage()
        self._clock = clock

    def get_run(self, run_id: str) -> RunState:
        state = self._storage.load_run(run_id)
        if state is None:
            raise GroundSealError(code="RUN_NOT_FOUND", message="Run not found", details={"run_id": run_id})
        return state

    def _store_checkpoint(self, checkpoint: Checkpoint) -> None:
        self._storage.save_checkpoint(checkpoint)

    def _execute_node_handler(self, node: NodeDefinition, state: RunState) -> dict[str, Any]:
        if node.handler == "prepare":
            return {"prepared": True, "step": "prepare"}
        if node.handler == "execute":
            return {"executed": True, "step": "execute"}
        raise GroundSealError(
            code="NODE_NOT_FOUND",
            message=f"Unknown handler: {node.handler}",
            details={"node_id": node.node_id},
        )

    def _advance_node(self, state: RunState, node: NodeDefinition) -> RunState | Interrupt:
        if state.status in TERMINAL_STATUSES:
            raise GroundSealError(
                code="RUN_TERMINAL",
                message="Cannot advance terminal run",
                details={"status": state.status.value},
            )

        state = state.model_copy(deep=True)
        state.status = RunStatus.RUNNING
        state.current_node_id = node.node_id
        state.updated_at = _now(self._clock)

        if node.requires_approval and not state.context.get("_approval_granted"):
            state.status = RunStatus.INTERRUPTED
            check_run_state_invariants(state)
            checkpoint = emit_checkpoint(
                state,
                reason=CheckpointReason.APPROVAL_REQUIRED,
                clock=self._clock,
            )
            self._store_checkpoint(checkpoint)
            self._storage.save_run(state)
            return Interrupt(
                run_id=state.run_id,
                checkpoint_id=checkpoint.checkpoint_id,
                reason="approval_required",
                node_id=node.node_id,
                message=f"Approval required for node {node.node_id}",
            )

        output = self._execute_node_handler(node, state)
        state.node_results[node.node_id] = NodeResult(
            node_id=node.node_id,
            status="completed",
            output=output,
            completed_at=_now(self._clock),
        )
        state.state_version += 1
        state.updated_at = _now(self._clock)
        check_run_state_invariants(state)
        return state

    def run(self, initial: RunInitialState) -> RunState | Interrupt:
        validate_run_initial(initial)

        if initial.workflow_id != FIXTURE_WORKFLOW_ID:
            raise GroundSealError(
                code="WORKFLOW_NOT_FOUND",
                message="Unknown workflow_id",
                details={"workflow_id": initial.workflow_id},
            )

        run_id = initial.run_id or str(uuid.uuid4())
        now = _now(self._clock)
        branch = branch_select(initial.context)

        state = RunState(
            run_id=run_id,
            state_version=0,
            status=RunStatus.PENDING,
            current_node_id=None,
            node_results={},
            branch_decisions=[branch],
            context=dict(initial.context),
            created_at=now,
            updated_at=now,
        )
        check_run_state_invariants(state)
        self._storage.save_run(state)

        for node in FIXTURE_NODES:
            current = self.get_run(run_id)
            result = self._advance_node(current, node)
            if isinstance(result, Interrupt):
                return result
            self._storage.save_run(result)

        final = self.get_run(run_id)
        final.status = RunStatus.COMPLETED
        final.current_node_id = None
        final.state_version += 1
        final.updated_at = _now(self._clock)
        check_run_state_invariants(final)
        self._storage.save_run(final)
        return final

    def resume(self, resume_input: ResumeInput) -> RunState | Interrupt:
        validate_resume_input(resume_input)
        state = self.get_run(resume_input.run_id)

        if state.status in TERMINAL_STATUSES:
            raise GroundSealError(
                code="RUN_TERMINAL",
                message="Cannot resume terminal run",
                details={"status": state.status.value},
            )

        if state.status != RunStatus.INTERRUPTED:
            raise GroundSealError(
                code="RUN_NOT_INTERRUPTED",
                message="Run is not in interrupted status",
                details={"status": state.status.value},
            )

        if not resume_input.approval.approved:
            failed = state.model_copy(deep=True)
            failed.status = RunStatus.FAILED
            failed.current_node_id = None
            failed.state_version += 1
            failed.updated_at = _now(self._clock)
            self._storage.save_run(failed)
            raise GroundSealError(
                code="APPROVAL_DENIED",
                message="Approval was denied",
                details={"approver_id": resume_input.approval.approver_id},
            )

        checkpoint_id = resume_input.checkpoint_id
        if checkpoint_id is None:
            ids = self._storage.list_checkpoint_ids(resume_input.run_id)
            if not ids:
                raise GroundSealError(
                    code="STALE_CHECKPOINT",
                    message="No checkpoint available for run",
                    details={"run_id": resume_input.run_id},
                )
            checkpoint_id = ids[-1]

        checkpoint = self._storage.load_checkpoint(checkpoint_id)
        if checkpoint is None:
            raise GroundSealError(
                code="STALE_CHECKPOINT",
                message="Checkpoint not found",
                details={"checkpoint_id": checkpoint_id},
            )

        if checkpoint.run_id != resume_input.run_id:
            raise GroundSealError(
                code="CHECKPOINT_RUN_MISMATCH",
                message="Checkpoint does not belong to run",
                details={"checkpoint_id": checkpoint_id, "run_id": resume_input.run_id},
            )

        if checkpoint.state_version < state.state_version:
            raise GroundSealError(
                code="STALE_CHECKPOINT",
                message="Checkpoint is stale relative to current run state",
                details={
                    "checkpoint_version": checkpoint.state_version,
                    "current_version": state.state_version,
                },
            )

        restored = checkpoint.state_snapshot.model_copy(deep=True)
        restored.context = dict(restored.context)
        restored.context["_approval_granted"] = True
        restored.context["approver_id"] = resume_input.approval.approver_id
        restored.status = RunStatus.RUNNING
        restored.state_version += 1
        restored.updated_at = _now(self._clock)
        check_run_state_invariants(restored)
        self._storage.save_run(restored)

        interrupted_node_id = restored.current_node_id
        if interrupted_node_id is None:
            raise GroundSealError(
                code="INVARIANT_VIOLATION",
                message="Interrupted state missing current_node_id",
            )

        node_def = next(n for n in FIXTURE_NODES if n.node_id == interrupted_node_id)
        output = self._execute_node_handler(node_def, restored)
        restored.node_results[interrupted_node_id] = NodeResult(
            node_id=interrupted_node_id,
            status="completed",
            output=output,
            completed_at=_now(self._clock),
        )
        restored.state_version += 1
        restored.updated_at = _now(self._clock)

        start_idx = next(i for i, n in enumerate(FIXTURE_NODES) if n.node_id == interrupted_node_id)
        for node in FIXTURE_NODES[start_idx + 1 :]:
            result = self._advance_node(restored, node)
            if isinstance(result, Interrupt):
                return result
            restored = result

        restored.status = RunStatus.COMPLETED
        restored.current_node_id = None
        restored.state_version += 1
        restored.updated_at = _now(self._clock)
        check_run_state_invariants(restored)
        self._storage.save_run(restored)
        return restored

    def apply_patch(self, state: RunState, patch: Patch) -> RunState:
        if self._storage.has_applied_patch(state.run_id, patch.patch_id):
            raise GroundSealError(
                code="DUPLICATE_PATCH",
                message="Patch already applied",
                details={"patch_id": patch.patch_id},
            )
        updated = apply_patch(state, patch, clock=self._clock)
        self._storage.mark_patch_applied(updated.run_id, patch.patch_id)
        self._storage.save_run(updated)
        return updated

    def emit_checkpoint(
        self,
        state: RunState,
        *,
        reason: CheckpointReason = CheckpointReason.SCHEDULED,
    ) -> Checkpoint:
        checkpoint = emit_checkpoint(state, reason=reason, clock=self._clock)
        self._storage.save_checkpoint(checkpoint)
        return checkpoint


class InMemoryRuntime(Runtime):
    """Backward-compatible alias using in-memory storage."""

    def __init__(self, *, clock: str | None = None) -> None:
        super().__init__(storage=MemoryStorage(), clock=clock)
