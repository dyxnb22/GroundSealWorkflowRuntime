"""Integration boundary tests for platform adapter."""

from __future__ import annotations

import pytest

from groundseal.adapter import PlatformAdapter, PlatformRunRequest
from groundseal.models import Approval, ResumeInput, RunInitialState, RunStatus
from groundseal.runtime import Runtime
from groundseal.storage import MemoryStorage

CLOCK = "2026-07-01T00:00:00Z"


@pytest.fixture
def adapter() -> PlatformAdapter:
    return PlatformAdapter(Runtime(storage=MemoryStorage(), clock=CLOCK))


class TestPlatformAdapter:
    def test_start_run_wraps_evidence(self, adapter: PlatformAdapter) -> None:
        req = PlatformRunRequest(
            tenant_id="tenant-a",
            caller_id="service-b",
            correlation_id="corr-123",
            initial=RunInitialState(
                workflow_id="fixture_approval_v1",
                run_id="adapter-run-001",
                context={"_approval_granted": True},
            ),
        )
        resp = adapter.start_run(req)
        assert resp.result_type == "run_state"
        assert resp.evidence.tenant_id == "tenant-a"
        assert resp.evidence.caller_id == "service-b"
        assert resp.run_state is not None
        assert resp.run_state.status == RunStatus.COMPLETED

    def test_tenant_id_not_in_run_state_context(self, adapter: PlatformAdapter) -> None:
        req = PlatformRunRequest(
            tenant_id="tenant-secret",
            caller_id="caller-1",
            initial=RunInitialState(
                workflow_id="fixture_approval_v1",
                run_id="adapter-run-002",
                context={"_approval_granted": True},
            ),
        )
        resp = adapter.start_run(req)
        assert resp.run_state is not None
        assert "tenant-secret" not in resp.run_state.context.values()

    def test_interrupt_flow_via_adapter(self, adapter: PlatformAdapter) -> None:
        req = PlatformRunRequest(
            tenant_id="tenant-a",
            caller_id="service-b",
            initial=RunInitialState(
                workflow_id="fixture_approval_v1",
                run_id="adapter-run-003",
                context={},
            ),
        )
        first = adapter.start_run(req)
        assert first.result_type == "interrupt"
        assert first.interrupt is not None

        resumed = adapter.resume_run(
            tenant_id="tenant-a",
            caller_id="service-b",
            resume_input=ResumeInput(
                run_id=first.interrupt.run_id,
                checkpoint_id=first.interrupt.checkpoint_id,
                approval=Approval(approved=True, approver_id="reviewer-x"),
            ),
        )
        assert resumed.result_type == "run_state"
        assert resumed.run_state is not None
        assert resumed.run_state.status == RunStatus.COMPLETED

    def test_missing_tenant_returns_adapter_error(self, adapter: PlatformAdapter) -> None:
        resp = adapter.resume_run(
            tenant_id="",
            caller_id="caller",
            resume_input=ResumeInput(
                run_id="x",
                approval=Approval(approved=True, approver_id="r"),
            ),
        )
        assert resp.result_type == "error"
        assert resp.error is not None
        assert resp.error["code"] == "INVALID_ADAPTER_REQUEST"

    def test_runtime_error_surfaces_as_adapter_error(self, adapter: PlatformAdapter) -> None:
        req = PlatformRunRequest(
            tenant_id="tenant-a",
            caller_id="service-b",
            initial=RunInitialState(workflow_id="unknown", context={}),
        )
        resp = adapter.start_run(req)
        assert resp.result_type == "error"
        assert resp.error is not None
        assert resp.error["code"] == "WORKFLOW_NOT_FOUND"
