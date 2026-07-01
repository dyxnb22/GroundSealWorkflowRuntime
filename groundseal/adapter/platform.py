"""Thin adapter wrapping runtime for parent platform callers."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from groundseal.errors import GroundSealError
from groundseal.models import Interrupt, ResumeInput, RunInitialState, RunState
from groundseal.runtime import Runtime


class PlatformRunRequest(BaseModel):
    """Adapter-local request envelope — tenancy stays outside core RunState."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: str = Field(min_length=1)
    caller_id: str = Field(min_length=1)
    initial: RunInitialState
    correlation_id: str | None = None


class PlatformEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: str
    caller_id: str
    correlation_id: str | None = None
    subsystem_version: str = "0.1.0"


class PlatformRunResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence: PlatformEvidence
    result_type: str
    run_state: RunState | None = None
    interrupt: Interrupt | None = None
    error: dict[str, Any] | None = None


class PlatformAdapter:
    """Boundary layer: validates adapter fields, delegates to runtime, wraps evidence."""

    def __init__(self, runtime: Runtime) -> None:
        self._runtime = runtime

    def start_run(self, request: PlatformRunRequest) -> PlatformRunResponse:
        evidence = PlatformEvidence(
            tenant_id=request.tenant_id,
            caller_id=request.caller_id,
            correlation_id=request.correlation_id,
        )
        try:
            outcome = self._runtime.run(request.initial)
        except GroundSealError as exc:
            return PlatformRunResponse(
                evidence=evidence,
                result_type="error",
                error=exc.to_dict(),
            )

        if isinstance(outcome, Interrupt):
            return PlatformRunResponse(
                evidence=evidence,
                result_type="interrupt",
                interrupt=outcome,
            )
        self._assert_no_tenant_leak(outcome, request.tenant_id)
        return PlatformRunResponse(
            evidence=evidence,
            result_type="run_state",
            run_state=outcome,
        )

    def resume_run(
        self,
        tenant_id: str,
        caller_id: str,
        resume_input: ResumeInput,
        *,
        correlation_id: str | None = None,
    ) -> PlatformRunResponse:
        evidence = PlatformEvidence(
            tenant_id=tenant_id,
            caller_id=caller_id,
            correlation_id=correlation_id,
        )
        if not tenant_id.strip() or not caller_id.strip():
            return PlatformRunResponse(
                evidence=evidence,
                result_type="error",
                error=GroundSealError(
                    code="INVALID_ADAPTER_REQUEST",
                    message="tenant_id and caller_id are required",
                ).to_dict(),
            )
        try:
            outcome = self._runtime.resume(resume_input)
        except GroundSealError as exc:
            return PlatformRunResponse(
                evidence=evidence,
                result_type="error",
                error=exc.to_dict(),
            )

        if isinstance(outcome, Interrupt):
            return PlatformRunResponse(
                evidence=evidence,
                result_type="interrupt",
                interrupt=outcome,
            )
        self._assert_no_tenant_leak(outcome, tenant_id)
        return PlatformRunResponse(
            evidence=evidence,
            result_type="run_state",
            run_state=outcome,
        )

    @staticmethod
    def _assert_no_tenant_leak(state: RunState, tenant_id: str) -> None:
        if tenant_id in state.context.values():
            raise GroundSealError(
                code="INVARIANT_VIOLATION",
                message="Adapter-local tenant_id must not appear in RunState context",
                details={"tenant_id": tenant_id},
            )
