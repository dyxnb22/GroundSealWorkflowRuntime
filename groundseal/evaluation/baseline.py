"""Deterministic evaluation scenarios and baseline comparison."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from groundseal.errors import GroundSealError
from groundseal.models import Approval, Interrupt, ResumeInput, RunInitialState, RunState, RunStatus
from groundseal.runtime import Runtime, branch_select
from groundseal.storage import MemoryStorage

CLOCK = "2026-07-01T00:00:00Z"


@dataclass
class ScenarioResult:
    category: str
    name: str
    passed: bool
    error_code: str | None = None
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvalReport:
    total: int
    passed: int
    failed: int
    scenarios: list[ScenarioResult]
    metrics: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "pass_rate": self.passed / self.total if self.total else 0.0,
            "metrics": self.metrics,
            "scenarios": [asdict(s) for s in self.scenarios],
        }


def _scenario_happy_path() -> ScenarioResult:
    rt = Runtime(storage=MemoryStorage(), clock=CLOCK)
    initial = RunInitialState(
        workflow_id="fixture_approval_v1",
        run_id="eval-happy-001",
        context={"branch_key": "a", "_approval_granted": True},
    )
    result = rt.run(initial)
    ok = isinstance(result, RunState) and result.status == RunStatus.COMPLETED
    return ScenarioResult("happy_path_run_complete", "linear_complete", ok)


def _scenario_interrupt_resume() -> ScenarioResult:
    rt = Runtime(storage=MemoryStorage(), clock=CLOCK)
    initial = RunInitialState(
        workflow_id="fixture_approval_v1",
        run_id="eval-interrupt-001",
        context={"branch_key": "a"},
    )
    first = rt.run(initial)
    if not isinstance(first, Interrupt):
        return ScenarioResult("interrupt_at_approval_then_resume", "approval_gate", False)
    resumed = rt.resume(
        ResumeInput(
            run_id=first.run_id,
            checkpoint_id=first.checkpoint_id,
            approval=Approval(approved=True, approver_id="eval-reviewer"),
        )
    )
    ok = isinstance(resumed, RunState) and resumed.status == RunStatus.COMPLETED
    return ScenarioResult("interrupt_at_approval_then_resume", "approval_gate", ok)


def _scenario_invalid_patch() -> ScenarioResult:
    from groundseal.models import Patch, RunState as RS

    state = RS(
        run_id="eval-patch-001",
        state_version=1,
        status=RunStatus.RUNNING,
        current_node_id="node_prepare",
        created_at=CLOCK,
        updated_at=CLOCK,
    )
    patch = Patch(
        patch_id="eval-patch-bad",
        target_version=99,
        operations=[{"op": "set", "path": "context.x", "value": 1}],
    )
    try:
        from groundseal.runtime import apply_patch

        apply_patch(state, patch, clock=CLOCK)
        return ScenarioResult("invalid_patch_rejected", "version_mismatch", False)
    except GroundSealError as exc:
        ok = exc.code == "VERSION_MISMATCH"
        return ScenarioResult(
            "invalid_patch_rejected",
            "version_mismatch",
            ok,
            error_code=exc.code,
        )


def _scenario_stale_checkpoint() -> ScenarioResult:
    rt = Runtime(storage=MemoryStorage(), clock=CLOCK)
    initial = RunInitialState(
        workflow_id="fixture_approval_v1",
        run_id="eval-stale-001",
        context={"branch_key": "a"},
    )
    interrupt = rt.run(initial)
    if not isinstance(interrupt, Interrupt):
        return ScenarioResult("resume_from_stale_checkpoint", "stale_reject", False)
    state = rt.get_run(interrupt.run_id)
    bumped = state.model_copy(deep=True)
    bumped.state_version += 5
    rt._storage.save_run(bumped)
    try:
        rt.resume(
            ResumeInput(
                run_id=interrupt.run_id,
                checkpoint_id=interrupt.checkpoint_id,
                approval=Approval(approved=True, approver_id="eval-reviewer"),
            )
        )
        return ScenarioResult("resume_from_stale_checkpoint", "stale_reject", False)
    except GroundSealError as exc:
        ok = exc.code == "STALE_CHECKPOINT"
        return ScenarioResult(
            "resume_from_stale_checkpoint",
            "stale_reject",
            ok,
            error_code=exc.code,
        )


def _scenario_branch_determinism() -> ScenarioResult:
    ctx = {"branch_key": "a", "seed": 42}
    a = branch_select(ctx)
    b = branch_select(ctx)
    ok = a.selected_edge == b.selected_edge and a.inputs_hash == b.inputs_hash
    return ScenarioResult("branch_determinism_same_input", "repeatable_branch", ok)


def _scenario_resume_not_interrupted() -> ScenarioResult:
    rt = Runtime(storage=MemoryStorage(), clock=CLOCK)
    initial = RunInitialState(
        workflow_id="fixture_approval_v1",
        run_id="eval-not-interrupted-001",
        context={"branch_key": "a", "_approval_granted": True},
    )
    rt.run(initial)
    try:
        rt.resume(
            ResumeInput(
                run_id="eval-not-interrupted-001",
                approval=Approval(approved=True, approver_id="eval-reviewer"),
            )
        )
        return ScenarioResult("failure_regression", "resume_not_interrupted", False)
    except GroundSealError as exc:
        ok = exc.code in ("RUN_NOT_INTERRUPTED", "RUN_TERMINAL")
        return ScenarioResult(
            "failure_regression",
            "resume_not_interrupted",
            ok,
            error_code=exc.code,
        )


def _scenario_invalid_resume_input() -> ScenarioResult:
    rt = Runtime(storage=MemoryStorage(), clock=CLOCK)
    try:
        rt.resume(
            ResumeInput(
                run_id="eval-bad-resume-001",
                approval=Approval(approved=True, approver_id=""),
            )
        )
        return ScenarioResult("failure_regression", "empty_approver_id", False)
    except GroundSealError as exc:
        ok = exc.code == "INVALID_RESUME_INPUT"
        return ScenarioResult(
            "failure_regression",
            "empty_approver_id",
            ok,
            error_code=exc.code,
        )


SCENARIO_RUNNERS = [
    _scenario_happy_path,
    _scenario_interrupt_resume,
    _scenario_invalid_patch,
    _scenario_stale_checkpoint,
    _scenario_branch_determinism,
    _scenario_resume_not_interrupted,
    _scenario_invalid_resume_input,
]


def run_evaluation() -> EvalReport:
    results = [fn() for fn in SCENARIO_RUNNERS]
    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed
    categories = {r.category for r in results}
    return EvalReport(
        total=len(results),
        passed=passed,
        failed=failed,
        scenarios=results,
        metrics={
            "categories_covered": len(categories),
            "negative_path_count": sum(
                1 for r in results if r.category == "failure_regression" or "invalid" in r.category
            ),
            "deterministic_clock": CLOCK,
        },
    )


def compare_to_baseline(
    report: EvalReport,
    baseline_path: Path | str,
    *,
    ratchet: bool = False,
    reason: str | None = None,
) -> dict[str, Any]:
    path = Path(baseline_path)
    current = report.to_dict()

    if not path.exists():
        if ratchet:
            path.parent.mkdir(parents=True, exist_ok=True)
            payload = {"baseline": current, "ratchet_reason": reason or "initial baseline"}
            path.write_text(json.dumps(payload, indent=2) + "\n")
            return {"status": "created", "path": str(path)}
        return {"status": "missing_baseline", "current": current}

    stored = json.loads(path.read_text())
    baseline = stored["baseline"]
    regression = []
    if current["passed"] < baseline["passed"]:
        regression.append("passed_count_decreased")
    if current["pass_rate"] < baseline["pass_rate"]:
        regression.append("pass_rate_decreased")

    if regression and not ratchet:
        return {
            "status": "regression",
            "regressions": regression,
            "baseline": baseline,
            "current": current,
        }

    if ratchet:
        stored["baseline"] = current
        stored["ratchet_reason"] = reason or "manual ratchet"
        path.write_text(json.dumps(stored, indent=2) + "\n")
        return {"status": "ratcheted", "path": str(path), "current": current}

    return {"status": "ok", "baseline": baseline, "current": current}
