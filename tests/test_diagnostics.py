"""Phase 7 diagnostics tests."""

from __future__ import annotations

import pytest

from groundseal.adapter import PlatformAdapter, PlatformRunRequest
from groundseal.diagnostics import build_diagnostic_report, build_run_summary, format_run_summary_text
from groundseal.models import RunInitialState
from groundseal.runtime import InMemoryRuntime
from tests.conftest import CLOCK, run_to_completion


class TestRunSummary:
    def test_summary_for_completed_run(self) -> None:
        rt = InMemoryRuntime(clock=CLOCK)
        initial = RunInitialState(
            workflow_id="fixture_approval_v1",
            run_id="diag-complete-001",
            context={"branch_key": "a"},
        )
        state = run_to_completion(rt, initial)
        summary = build_run_summary(state)
        assert summary.status == "completed"
        assert len(summary.nodes) == 2
        assert "completed" in summary.narrative
        assert "_approval_granted" not in summary.context_keys

    def test_summary_for_interrupted_run(self) -> None:
        rt = InMemoryRuntime(clock=CLOCK)
        initial = RunInitialState(
            workflow_id="fixture_approval_v1",
            run_id="diag-interrupt-001",
            context={},
        )
        interrupt = rt.run(initial)
        state = rt.get_run(interrupt.run_id)
        cps = rt.list_checkpoints(interrupt.run_id)
        summary = build_run_summary(state, cps)
        assert summary.status == "interrupted"
        assert summary.workflow_phase.startswith("awaiting_approval_at:")
        assert len(summary.checkpoints) >= 1

    def test_format_text_is_human_readable(self) -> None:
        rt = InMemoryRuntime(clock=CLOCK)
        initial = RunInitialState(
            workflow_id="fixture_approval_v1",
            run_id="diag-text-001",
            context={},
        )
        state = run_to_completion(rt, initial)
        text = format_run_summary_text(build_run_summary(state))
        assert "Run Summary" in text
        assert "node_prepare" in text


class TestDiagnosticReport:
    def test_build_diagnostic_report(self) -> None:
        rt = InMemoryRuntime(clock=CLOCK)
        initial = RunInitialState(
            workflow_id="fixture_approval_v1",
            run_id="diag-report-001",
            context={},
        )
        interrupt = rt.run(initial)
        report = build_diagnostic_report(rt, interrupt.run_id)
        assert report.invariant_status == "ok"
        assert report.raw_status == "interrupted"
        assert any("approval" in h.lower() for h in report.review_hints)

    def test_adapter_includes_diagnostic_when_requested(self) -> None:
        adapter = PlatformAdapter(InMemoryRuntime(clock=CLOCK))
        resp = adapter.start_run(
            PlatformRunRequest(
                tenant_id="t1",
                caller_id="c1",
                initial=RunInitialState(
                    workflow_id="fixture_approval_v1",
                    run_id="diag-adapter-001",
                    context={},
                ),
            ),
            include_diagnostic=True,
        )
        assert resp.result_type == "interrupt"
        assert resp.diagnostic is not None
        assert resp.diagnostic.summary.run_id == "diag-adapter-001"

    def test_adapter_resume_includes_diagnostic(self) -> None:
        from groundseal.models import Approval, ResumeInput

        adapter = PlatformAdapter(InMemoryRuntime(clock=CLOCK))
        first = adapter.start_run(
            PlatformRunRequest(
                tenant_id="t1",
                caller_id="c1",
                initial=RunInitialState(
                    workflow_id="fixture_approval_v1",
                    run_id="diag-adapter-resume",
                    context={},
                ),
            )
        )
        assert first.interrupt is not None
        resumed = adapter.resume_run(
            tenant_id="t1",
            caller_id="c1",
            resume_input=ResumeInput(
                run_id=first.interrupt.run_id,
                approval=Approval(approved=True, approver_id="reviewer"),
            ),
            include_diagnostic=True,
        )
        assert resumed.diagnostic is not None
        assert resumed.diagnostic.summary.status == "completed"

    def test_adapter_get_diagnostic_report(self) -> None:
        adapter = PlatformAdapter(InMemoryRuntime(clock=CLOCK))
        run_id = "diag-adapter-002"
        adapter.start_run(
            PlatformRunRequest(
                tenant_id="t1",
                caller_id="c1",
                initial=RunInitialState(
                    workflow_id="fixture_approval_v1",
                    run_id=run_id,
                    context={},
                ),
            )
        )
        report = adapter.get_diagnostic_report(run_id)
        assert report.summary.status == "interrupted"

    def test_diagnostic_unknown_run_raises(self) -> None:
        from groundseal.errors import GroundSealError

        rt = InMemoryRuntime(clock=CLOCK)
        with pytest.raises(GroundSealError):
            build_diagnostic_report(rt, "00000000-0000-0000-0000-000000000099")
