"""Approver authorization for adapter-layer IdP integration."""

from __future__ import annotations

from typing import Callable, Protocol

from groundseal.errors import GroundSealError


class ApproverValidator(Protocol):
    """Validate approver_id against tenant/platform policy before resume."""

    def validate(self, *, tenant_id: str, approver_id: str, run_id: str) -> None: ...


class AllowListApproverValidator:
    """Deterministic validator for tests and simple deployments."""

    def __init__(self, allowed: set[str] | frozenset[str]) -> None:
        self._allowed = frozenset(allowed)

    def validate(self, *, tenant_id: str, approver_id: str, run_id: str) -> None:
        if approver_id not in self._allowed:
            raise GroundSealError(
                code="APPROVER_UNAUTHORIZED",
                message="approver_id is not authorized for this tenant",
                details={"tenant_id": tenant_id, "approver_id": approver_id, "run_id": run_id},
            )


class CallableApproverValidator:
    """Wrap parent-platform IdP callback."""

    def __init__(self, fn: Callable[..., bool]) -> None:
        self._fn = fn

    def validate(self, *, tenant_id: str, approver_id: str, run_id: str) -> None:
        allowed = self._fn(tenant_id=tenant_id, approver_id=approver_id, run_id=run_id)
        if not allowed:
            raise GroundSealError(
                code="APPROVER_UNAUTHORIZED",
                message="approver_id rejected by external validator",
                details={"tenant_id": tenant_id, "approver_id": approver_id, "run_id": run_id},
            )
