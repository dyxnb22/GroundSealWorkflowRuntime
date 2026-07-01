"""Workflow runtime engine."""

from __future__ import annotations

import uuid
from typing import Any

from groundseal.errors import GroundSealError
from groundseal.invariants import check_run_state_invariants
from groundseal.models import (
    TERMINAL_STATUSES,
    ApprovalDenialPolicy,
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
from groundseal.runtime.branching import branch_select
from groundseal.runtime.checkpointing import emit_checkpoint
from groundseal.runtime.patching import apply_patch
from groundseal.runtime.timeutil import now
from groundseal.storage import MemoryStorage, StorageBackend
from groundseal.validation import sanitize_caller_context, validate_resume_input, validate_run_initial
from groundseal.workflow import WorkflowDefinition, WorkflowRegistry, default_registry


class Runtime:
    """Workflow runtime with pluggable storage and workflow registry."""

    def __init__(
        self,
        *,
        storage: StorageBackend | None = None,
        clock: str | None = None,
        denial_policy: ApprovalDenialPolicy = ApprovalDenialPolicy.FAIL_RUN,
        workflow_registry: WorkflowRegistry | None = None,
    ) -> None:
        self._storage = storage or MemoryStorage()
        self._clock = clock
        self._denial_policy = denial_policy
        self._workflows = workflow_registry or default_registry()

    def get_run(self, run_id: str) -> RunState:
        state = self._storage.load_run(run_id)
        if state is None:
            raise GroundSealError(code="RUN_NOT_FOUND", message="Run not found", details={"run_id": run_id})
        return state

    def persist_run(self, state: RunState) -> None:
        check_run_state_invariants(state)
        self._storage.save_run(state)

    def _workflow_for_state(self, state: RunState) -> WorkflowDefinition:
        workflow_id = state.context.get("_workflow_id")
        if not isinstance(workflow_id, str):
            raise GroundSealError(
                code="INVARIANT_VIOLATION",
                message="Run state missing _workflow_id",
                details={"run_id": state.run_id},
            )
        return self._workflows.get(workflow_id)

    def _find_node(self, workflow: WorkflowDefinition, node_id: str) -> NodeDefinition:
        for node in workflow.nodes:
            if node.node_id == node_id:
                return node
        raise GroundSealError(
            code="NODE_NOT_FOUND",
            message=f"Unknown node_id: {node_id}",
            details={"node_id": node_id, "workflow_id": workflow.workflow_id},
        )

    def _finalize_run(self, state: RunState) -> RunState:
        state = state.model_copy(deep=True)
        state.status = RunStatus.COMPLETED
        state.current_node_id = None
        state.state_version += 1
        state.updated_at = now(self._clock)
        check_run_state_invariants(state)
        self._storage.save_run(state)
        return state

    def _execute_node_handler(self, node: NodeDefinition) -> dict[str, Any]:
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
        state.updated_at = now(self._clock)

        if node.requires_approval and not state.context.get("_approval_granted"):
            state.status = RunStatus.INTERRUPTED
            check_run_state_invariants(state)
            checkpoint = emit_checkpoint(
                state,
                reason=CheckpointReason.APPROVAL_REQUIRED,
                clock=self._clock,
            )
            self._storage.save_checkpoint(checkpoint)
            self._storage.save_run(state)
            return Interrupt(
                run_id=state.run_id,
                checkpoint_id=checkpoint.checkpoint_id,
                reason="approval_required",
                node_id=node.node_id,
                message=f"Approval required for node {node.node_id}",
            )

        output = self._execute_node_handler(node)
        state.node_results[node.node_id] = NodeResult(
            node_id=node.node_id,
            status="completed",
            output=output,
            completed_at=now(self._clock),
        )
        state.state_version += 1
        state.updated_at = now(self._clock)
        check_run_state_invariants(state)
        return state

    def run(self, initial: RunInitialState) -> RunState | Interrupt:
        validate_run_initial(initial)
        workflow = self._workflows.get(initial.workflow_id)

        run_id = initial.run_id or str(uuid.uuid4())
        ts = now(self._clock)
        branch = branch_select(sanitize_caller_context(initial.context))

        context = sanitize_caller_context(initial.context)
        context["_workflow_id"] = workflow.workflow_id

        state = RunState(
            run_id=run_id,
            state_version=0,
            status=RunStatus.PENDING,
            current_node_id=None,
            node_results={},
            branch_decisions=[branch],
            context=context,
            created_at=ts,
            updated_at=ts,
        )
        check_run_state_invariants(state)
        self._storage.save_run(state)

        current = state
        for node in workflow.nodes:
            result = self._advance_node(current, node)
            if isinstance(result, Interrupt):
                return result
            current = result
            self._storage.save_run(current)

        return self._finalize_run(current)

    def resume(self, resume_input: ResumeInput) -> RunState | Interrupt:
        validate_resume_input(resume_input)
        state = self.get_run(resume_input.run_id)
        workflow = self._workflow_for_state(state)

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
            if self._denial_policy == ApprovalDenialPolicy.REMAIN_INTERRUPTED:
                raise GroundSealError(
                    code="APPROVAL_DENIED",
                    message="Approval was denied; run remains interrupted",
                    details={
                        "approver_id": resume_input.approval.approver_id,
                        "policy": self._denial_policy.value,
                    },
                )
            failed = state.model_copy(deep=True)
            failed.status = RunStatus.FAILED
            failed.current_node_id = None
            failed.state_version += 1
            failed.updated_at = now(self._clock)
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
                    code="CHECKPOINT_NOT_FOUND",
                    message="No checkpoint available for run",
                    details={"run_id": resume_input.run_id},
                )
            checkpoint_id = ids[-1]

        checkpoint = self._storage.load_checkpoint(checkpoint_id)
        if checkpoint is None:
            raise GroundSealError(
                code="CHECKPOINT_NOT_FOUND",
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
        restored.updated_at = now(self._clock)
        check_run_state_invariants(restored)
        self._storage.save_run(restored)

        interrupted_node_id = restored.current_node_id
        if interrupted_node_id is None:
            raise GroundSealError(
                code="INVARIANT_VIOLATION",
                message="Interrupted state missing current_node_id",
            )

        node_def = self._find_node(workflow, interrupted_node_id)
        output = self._execute_node_handler(node_def)
        restored.node_results[interrupted_node_id] = NodeResult(
            node_id=interrupted_node_id,
            status="completed",
            output=output,
            completed_at=now(self._clock),
        )
        restored.state_version += 1
        restored.updated_at = now(self._clock)

        start_idx = next(i for i, n in enumerate(workflow.nodes) if n.node_id == interrupted_node_id)
        current = restored
        for node in workflow.nodes[start_idx + 1 :]:
            result = self._advance_node(current, node)
            if isinstance(result, Interrupt):
                return result
            current = result

        return self._finalize_run(current)

    def apply_patch(self, state: RunState, patch: Patch) -> RunState:
        if self._storage.has_applied_patch(state.run_id, patch.patch_id):
            raise GroundSealError(
                code="DUPLICATE_PATCH",
                message="Patch already applied",
                details={"patch_id": patch.patch_id},
            )
        updated = apply_patch(state, patch, clock=self._clock)
        self._storage.save_run(updated)
        self._storage.mark_patch_applied(updated.run_id, patch.patch_id)
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

    def list_checkpoints(self, run_id: str) -> list[Checkpoint]:
        result: list[Checkpoint] = []
        for cp_id in self._storage.list_checkpoint_ids(run_id):
            cp = self._storage.load_checkpoint(cp_id)
            if cp is not None:
                result.append(cp)
        return result


class InMemoryRuntime(Runtime):
    """Backward-compatible alias using in-memory storage."""

    def __init__(
        self,
        *,
        clock: str | None = None,
        denial_policy: ApprovalDenialPolicy = ApprovalDenialPolicy.FAIL_RUN,
        workflow_registry: WorkflowRegistry | None = None,
    ) -> None:
        super().__init__(
            storage=MemoryStorage(),
            clock=clock,
            denial_policy=denial_policy,
            workflow_registry=workflow_registry,
        )
