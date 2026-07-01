"""Diagnostic report models and builders for operator/reviewer consumption."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field

from groundseal.errors import GroundSealError
from groundseal.invariants import check_run_state_invariants
from groundseal.models import Checkpoint, RunState, RunStatus

if TYPE_CHECKING:
    from groundseal.diagnostics import RunReader


class NodeSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    node_id: str
    status: str
    output_keys: list[str] = Field(default_factory=list)
    completed_at: str | None = None


class CheckpointSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    checkpoint_id: str
    state_version: int
    reason: str
    emitted_at: str


class BranchSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision_id: str
    selected_edge: str
    inputs_hash: str


class RunSummary(BaseModel):
    """Human-reviewable summary derived from RunState."""

    model_config = ConfigDict(extra="forbid")

    run_id: str
    status: str
    state_version: int
    current_node_id: str | None
    workflow_phase: str
    nodes: list[NodeSummary] = Field(default_factory=list)
    checkpoints: list[CheckpointSummary] = Field(default_factory=list)
    branches: list[BranchSummary] = Field(default_factory=list)
    context_keys: list[str] = Field(default_factory=list)
    created_at: str
    updated_at: str
    narrative: str


class DiagnosticReport(BaseModel):
    """Full diagnostic artifact for a run."""

    model_config = ConfigDict(extra="forbid")

    run_id: str
    summary: RunSummary
    invariant_status: str
    review_hints: list[str] = Field(default_factory=list)
    raw_status: str


def _workflow_phase(state: RunState) -> str:
    if state.status == RunStatus.INTERRUPTED:
        return f"awaiting_approval_at:{state.current_node_id}"
    if state.status == RunStatus.COMPLETED:
        return "completed"
    if state.status == RunStatus.FAILED:
        return "failed"
    if state.status == RunStatus.RUNNING:
        return f"executing:{state.current_node_id}"
    return state.status.value


def _build_narrative(state: RunState, checkpoints: list[Checkpoint]) -> str:
    completed = [n for n in state.node_results.values() if n.status == "completed"]
    parts = [
        f"Run {state.run_id} is {state.status.value} at version {state.state_version}.",
        f"Completed nodes: {len(completed)}.",
    ]
    if state.status == RunStatus.INTERRUPTED:
        parts.append(f"Paused at {state.current_node_id} pending approval.")
    if checkpoints:
        latest = checkpoints[-1]
        parts.append(f"Latest checkpoint {latest.checkpoint_id} ({latest.reason.value}) at v{latest.state_version}.")
    if state.branch_decisions:
        edge = state.branch_decisions[-1].selected_edge
        parts.append(f"Branch selected edge: {edge}.")
    return " ".join(parts)


def build_run_summary(state: RunState, checkpoints: list[Checkpoint] | None = None) -> RunSummary:
    cps = checkpoints or []
    nodes = [
        NodeSummary(
            node_id=nr.node_id,
            status=nr.status,
            output_keys=sorted(nr.output.keys()),
            completed_at=nr.completed_at,
        )
        for nr in state.node_results.values()
    ]
    cp_summaries = [
        CheckpointSummary(
            checkpoint_id=cp.checkpoint_id,
            state_version=cp.state_version,
            reason=cp.reason.value,
            emitted_at=cp.emitted_at,
        )
        for cp in cps
    ]
    branches = [
        BranchSummary(
            decision_id=b.decision_id,
            selected_edge=b.selected_edge,
            inputs_hash=b.inputs_hash[:12] + "...",
        )
        for b in state.branch_decisions
    ]
    return RunSummary(
        run_id=state.run_id,
        status=state.status.value,
        state_version=state.state_version,
        current_node_id=state.current_node_id,
        workflow_phase=_workflow_phase(state),
        nodes=nodes,
        checkpoints=cp_summaries,
        branches=branches,
        context_keys=sorted(k for k in state.context.keys() if not k.startswith("_")),
        created_at=state.created_at,
        updated_at=state.updated_at,
        narrative=_build_narrative(state, cps),
    )


def format_run_summary_text(summary: RunSummary) -> str:
    lines = [
        f"=== Run Summary: {summary.run_id} ===",
        f"Status: {summary.status} | Version: {summary.state_version}",
        f"Phase: {summary.workflow_phase}",
        "",
        summary.narrative,
        "",
        "Nodes:",
    ]
    if summary.nodes:
        for n in summary.nodes:
            keys = ", ".join(n.output_keys) or "(none)"
            lines.append(f"  - {n.node_id}: {n.status} [outputs: {keys}]")
    else:
        lines.append("  (none completed)")

    lines.append("")
    lines.append("Checkpoints:")
    if summary.checkpoints:
        for cp in summary.checkpoints:
            lines.append(f"  - {cp.checkpoint_id} v{cp.state_version} ({cp.reason})")
    else:
        lines.append("  (none)")

    lines.append("")
    lines.append(f"Context keys: {', '.join(summary.context_keys) or '(empty)'}")
    return "\n".join(lines)


def _review_hints(state: RunState) -> list[str]:
    hints: list[str] = []
    if state.status == RunStatus.INTERRUPTED:
        hints.append("Action required: obtain approval and call resume().")
    if state.status == RunStatus.FAILED:
        hints.append("Run failed; inspect node_results and error logs before retry.")
    if not state.node_results:
        hints.append("No nodes completed yet; run may have interrupted early.")
    if state.context.get("_approval_granted"):
        hints.append("Approval was granted; visible in context.")
    return hints


def build_diagnostic_report(reader: RunReader, run_id: str) -> DiagnosticReport:
    state = reader.get_run(run_id)
    checkpoints = reader.list_checkpoints(run_id)
    summary = build_run_summary(state, checkpoints)
    invariant_status = "ok"
    try:
        check_run_state_invariants(state)
    except GroundSealError:
        invariant_status = "violation"

    return DiagnosticReport(
        run_id=run_id,
        summary=summary,
        invariant_status=invariant_status,
        review_hints=_review_hints(state),
        raw_status=state.status.value,
    )
