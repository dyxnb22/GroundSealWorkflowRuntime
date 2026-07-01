"""Integration boundary tests for platform adapter."""

from __future__ import annotations

import pytest

from groundseal.adapter import PlatformAdapter, PlatformRunRequest
from groundseal.errors import GroundSealError
from groundseal.models import Approval, ResumeInput, RunInitialState, RunStatus
from groundseal.runtime import Runtime
from groundseal.storage import MemoryStorage
from tests.conftest import CLOCK, run_to_completion


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
                context={"branch_key": "a"},
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
                approval=Approval(approved=True, approver_id="reviewer"),
            ),
        )
        assert resumed.result_type == "run_state"
        assert resumed.evidence.tenant_id == "tenant-a"
        assert resumed.run_state is not None
        assert resumed.run_state.status == RunStatus.COMPLETED

    def test_tenant_id_not_in_run_state_context(self, adapter: PlatformAdapter) -> None:
        req = PlatformRunRequest(
            tenant_id="tenant-secret",
            caller_id="caller-1",
            initial=RunInitialState(
                workflow_id="fixture_approval_v1",
                run_id="adapter-run-002",
                context={},
            ),
        )
        rt = adapter._runtime
        state = run_to_completion(rt, req.initial)
        assert "tenant-secret" not in state.context
        assert "tenant-secret" not in state.context.values()

    def test_tenant_as_context_key_rejected_by_adapter(self, adapter: PlatformAdapter) -> None:
        req = PlatformRunRequest(
            tenant_id="tenant-secret",
            caller_id="caller-1",
            initial=RunInitialState(
                workflow_id="fixture_approval_v1",
                run_id="adapter-run-leak",
                context={"tenant-secret": "leaked"},
            ),
        )
        resp = adapter.start_run(req)
        assert resp.result_type == "error"
        assert resp.error is not None
        assert resp.error["code"] == "INVALID_ADAPTER_REQUEST"

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
