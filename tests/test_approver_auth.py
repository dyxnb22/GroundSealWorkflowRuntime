"""Approver authorization at adapter boundary."""

from __future__ import annotations

import pytest

from groundseal.adapter import AllowListApproverValidator, CallableApproverValidator, PlatformAdapter, PlatformRunRequest
from groundseal.errors import GroundSealError
from groundseal.models import Approval, ResumeInput, RunInitialState, RunStatus
from groundseal.runtime import Runtime
from groundseal.storage import MemoryStorage
from tests.conftest import CLOCK


@pytest.fixture
def adapter_with_allowlist() -> PlatformAdapter:
    validator = AllowListApproverValidator({"reviewer-a", "reviewer-b"})
    return PlatformAdapter(
        Runtime(storage=MemoryStorage(), clock=CLOCK),
        approver_validator=validator,
    )


class TestAllowListApproverValidator:
    def test_allowed_approver_passes(self) -> None:
        validator = AllowListApproverValidator({"alice"})
        validator.validate(tenant_id="t1", approver_id="alice", run_id="run-1")

    def test_unauthorized_approver_raises(self) -> None:
        validator = AllowListApproverValidator({"alice"})
        with pytest.raises(GroundSealError) as exc:
            validator.validate(tenant_id="t1", approver_id="bob", run_id="run-1")
        assert exc.value.code == "APPROVER_UNAUTHORIZED"


class TestCallableApproverValidator:
    def test_callback_rejection(self) -> None:
        def deny(**kwargs: object) -> bool:
            return False

        validator = CallableApproverValidator(deny)
        with pytest.raises(GroundSealError) as exc:
            validator.validate(tenant_id="t1", approver_id="x", run_id="run-1")
        assert exc.value.code == "APPROVER_UNAUTHORIZED"

    def test_callback_approval(self) -> None:
        def allow(**kwargs: object) -> bool:
            return kwargs.get("approver_id") == "trusted"

        validator = CallableApproverValidator(allow)
        validator.validate(tenant_id="t1", approver_id="trusted", run_id="run-1")


class TestAdapterApproverAuth:
    def _interrupt(self, adapter: PlatformAdapter):
        req = PlatformRunRequest(
            tenant_id="tenant-a",
            caller_id="service-b",
            initial=RunInitialState(
                workflow_id="fixture_approval_v1",
                run_id="auth-run-001",
                context={},
            ),
        )
        first = adapter.start_run(req)
        assert first.result_type == "interrupt"
        return first

    def test_unauthorized_resume_rejected(self, adapter_with_allowlist: PlatformAdapter) -> None:
        first = self._interrupt(adapter_with_allowlist)
        resp = adapter_with_allowlist.resume_run(
            tenant_id="tenant-a",
            caller_id="service-b",
            resume_input=ResumeInput(
                run_id=first.interrupt.run_id,
                checkpoint_id=first.interrupt.checkpoint_id,
                approval=Approval(approved=True, approver_id="unknown-reviewer"),
            ),
        )
        assert resp.result_type == "error"
        assert resp.error is not None
        assert resp.error["code"] == "APPROVER_UNAUTHORIZED"

    def test_authorized_resume_succeeds(self, adapter_with_allowlist: PlatformAdapter) -> None:
        first = self._interrupt(adapter_with_allowlist)
        resp = adapter_with_allowlist.resume_run(
            tenant_id="tenant-a",
            caller_id="service-b",
            resume_input=ResumeInput(
                run_id=first.interrupt.run_id,
                checkpoint_id=first.interrupt.checkpoint_id,
                approval=Approval(approved=True, approver_id="reviewer-a"),
            ),
        )
        assert resp.result_type == "run_state"
        assert resp.run_state is not None
        assert resp.run_state.status == RunStatus.COMPLETED

    def test_denied_approval_skips_validator(self, adapter_with_allowlist: PlatformAdapter) -> None:
        first = self._interrupt(adapter_with_allowlist)
        resp = adapter_with_allowlist.resume_run(
            tenant_id="tenant-a",
            caller_id="service-b",
            resume_input=ResumeInput(
                run_id=first.interrupt.run_id,
                checkpoint_id=first.interrupt.checkpoint_id,
                approval=Approval(approved=False, approver_id="unknown-reviewer"),
            ),
        )
        assert resp.result_type == "error"
        assert resp.error is not None
        assert resp.error["code"] == "APPROVAL_DENIED"
