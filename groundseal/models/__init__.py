"""Pydantic models aligned to docs/contracts/."""

from __future__ import annotations

import json
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ApprovalDenialPolicy(str, Enum):
    """Phase 8 experiment: behavior when approval is denied."""

    FAIL_RUN = "fail_run"
    REMAIN_INTERRUPTED = "remain_interrupted"


class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    INTERRUPTED = "interrupted"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


TERMINAL_STATUSES = {RunStatus.COMPLETED, RunStatus.FAILED, RunStatus.CANCELLED}


class NodeStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    INTERRUPTED = "interrupted"


class NodeResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    node_id: str
    status: str
    output: dict[str, Any] = Field(default_factory=dict)
    completed_at: str


class BranchDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision_id: str
    inputs_hash: str
    selected_edge: str


class RunState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    state_version: int = Field(ge=0)
    status: RunStatus
    current_node_id: str | None
    node_results: dict[str, NodeResult] = Field(default_factory=dict)
    branch_decisions: list[BranchDecision] = Field(default_factory=list)
    context: dict[str, Any] = Field(default_factory=dict)
    created_at: str
    updated_at: str


class RunInitialState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workflow_id: str
    context: dict[str, Any] = Field(default_factory=dict)
    run_id: str | None = None


class PatchOperation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    op: str
    path: str
    value: Any | None = None


class Patch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    patch_id: str
    target_version: int = Field(ge=0)
    operations: list[PatchOperation]


class CheckpointReason(str, Enum):
    SCHEDULED = "scheduled"
    APPROVAL_REQUIRED = "approval_required"
    MANUAL = "manual"


class Checkpoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    checkpoint_id: str
    run_id: str
    state_version: int = Field(ge=0)
    state_snapshot: RunState
    reason: CheckpointReason
    emitted_at: str


class Interrupt(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    checkpoint_id: str
    reason: str
    node_id: str
    message: str


class Approval(BaseModel):
    model_config = ConfigDict(extra="forbid")

    approved: bool
    approver_id: str


class ResumeInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    approval: Approval
    checkpoint_id: str | None = None


class NodeDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    node_id: str
    requires_approval: bool
    handler: str


def export_schemas(output_dir: str = "schemas") -> None:
    """Export JSON schemas for integration consumers."""
    import pathlib

    models: list[type[BaseModel]] = [
        RunState,
        RunInitialState,
        Patch,
        Checkpoint,
        Interrupt,
        ResumeInput,
    ]
    out = pathlib.Path(output_dir)
    out.mkdir(exist_ok=True)
    for model in models:
        path = out / f"{model.__name__.lower()}.schema.json"
        path.write_text(json.dumps(model.model_json_schema(), indent=2) + "\n")
