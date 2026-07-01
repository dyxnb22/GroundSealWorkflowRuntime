"""Controlled comparative experiments (Phase 8)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from groundseal.errors import GroundSealError
from groundseal.models import Approval, ApprovalDenialPolicy, Interrupt, ResumeInput, RunInitialState, RunStatus
from groundseal.runtime import Runtime
from groundseal.storage import FileStorage, MemoryStorage

CLOCK = "2026-07-01T00:00:00Z"
RUN_ID = "experiment-run-001"


@dataclass
class StorageBackendComparison:
    backend: str
    completes: bool
    survives_restart: bool
    checkpoint_count: int
    file_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ApprovalPolicyComparison:
    policy: str
    status_after_deny: str
    can_retry_resume: bool
    error_code: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ExperimentReport:
    hypothesis: str
    observations: list[dict[str, Any]] = field(default_factory=list)
    conclusion: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _run_interrupt_flow(runtime: Runtime, run_id: str) -> tuple[bool, int]:
    initial = RunInitialState(
        workflow_id="fixture_approval_v1",
        run_id=run_id,
        context={"branch_key": "a"},
    )
    outcome = runtime.run(initial)
    if not isinstance(outcome, Interrupt):
        return False, 0
    try:
        runtime.resume(
            ResumeInput(
                run_id=run_id,
                checkpoint_id=outcome.checkpoint_id,
                approval=Approval(approved=True, approver_id="exp-reviewer"),
            )
        )
        return True, len(runtime.list_checkpoints(run_id))
    except GroundSealError:
        return False, len(runtime.list_checkpoints(run_id))


def run_storage_backend_experiment(tmp_dir: Path | None = None) -> ExperimentReport:
    """Compare MemoryStorage vs FileStorage on restart survival."""
    mem_rt = Runtime(storage=MemoryStorage(), clock=CLOCK)
    mem_completes, mem_cps = _run_interrupt_flow(mem_rt, "exp-mem-001")

    file_root = tmp_dir or Path("/tmp/groundseal_exp_storage")
    if file_root.exists():
        for p in file_root.rglob("*"):
            if p.is_file():
                p.unlink()

    file_rt = Runtime(storage=FileStorage(file_root), clock=CLOCK)
    file_rt.run(
        RunInitialState(
            workflow_id="fixture_approval_v1",
            run_id=RUN_ID,
            context={"branch_key": "a"},
        )
    )

    file_rt2 = Runtime(storage=FileStorage(file_root), clock=CLOCK)
    state = file_rt2.get_run(RUN_ID)
    restart_ok = state.status == RunStatus.INTERRUPTED
    if restart_ok:
        cps = file_rt2.list_checkpoints(RUN_ID)
        if cps:
            try:
                file_rt2.resume(
                    ResumeInput(
                        run_id=RUN_ID,
                        checkpoint_id=cps[-1].checkpoint_id,
                        approval=Approval(approved=True, approver_id="exp-reviewer"),
                    )
                )
                restart_ok = file_rt2.get_run(RUN_ID).status == RunStatus.COMPLETED
            except GroundSealError:
                restart_ok = False

    file_count = sum(1 for _ in file_root.rglob("*.json")) if file_root.exists() else 0

    observations = [
        StorageBackendComparison(
            backend="memory",
            completes=mem_completes,
            survives_restart=False,
            checkpoint_count=mem_cps,
            file_count=0,
        ).to_dict(),
        StorageBackendComparison(
            backend="file",
            completes=restart_ok,
            survives_restart=restart_ok,
            checkpoint_count=len(file_rt2.list_checkpoints(RUN_ID)),
            file_count=file_count,
        ).to_dict(),
    ]

    return ExperimentReport(
        hypothesis="FileStorage enables cross-session resume; MemoryStorage does not persist across processes.",
        observations=observations,
        conclusion="FileStorage adds durability and restart survival at the cost of file artifacts; MemoryStorage remains default for tests.",
    )


def run_approval_policy_experiment() -> ExperimentReport:
    """Compare FAIL_RUN vs REMAIN_INTERRUPTED on approval denial."""
    results: list[ApprovalPolicyComparison] = []

    for policy in (ApprovalDenialPolicy.FAIL_RUN, ApprovalDenialPolicy.REMAIN_INTERRUPTED):
        rt = Runtime(storage=MemoryStorage(), clock=CLOCK, denial_policy=policy)
        run_id = f"exp-deny-{policy.value}"
        initial = RunInitialState(workflow_id="fixture_approval_v1", run_id=run_id, context={})
        interrupt = rt.run(initial)
        assert isinstance(interrupt, Interrupt), "Expected interrupt at approval gate"

        error_code = ""
        try:
            rt.resume(
                ResumeInput(
                    run_id=interrupt.run_id,
                    checkpoint_id=interrupt.checkpoint_id,
                    approval=Approval(approved=False, approver_id="denier"),
                )
            )
        except GroundSealError as exc:
            error_code = exc.code

        state = rt.get_run(interrupt.run_id)
        can_retry = False
        if state.status == RunStatus.INTERRUPTED:
            try:
                rt.resume(
                    ResumeInput(
                        run_id=interrupt.run_id,
                        checkpoint_id=interrupt.checkpoint_id,
                        approval=Approval(approved=True, approver_id="approver"),
                    )
                )
                can_retry = rt.get_run(interrupt.run_id).status == RunStatus.COMPLETED
            except GroundSealError:
                can_retry = False

        results.append(
            ApprovalPolicyComparison(
                policy=policy.value,
                status_after_deny=state.status.value,
                can_retry_resume=can_retry,
                error_code=error_code,
            )
        )

    return ExperimentReport(
        hypothesis="REMAIN_INTERRUPTED allows re-approval after denial; FAIL_RUN closes the run.",
        observations=[r.to_dict() for r in results],
        conclusion="Default FAIL_RUN for audit clarity; REMAIN_INTERRUPTED available when operators need retry without new run.",
    )
