# Adapter Contract (Phase 5)

Parent platform integration surface. Core runtime types remain in [public-api.md](public-api.md).

## PlatformRunRequest (adapter-local envelope)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `tenant_id` | string | yes | Not stored in RunState |
| `caller_id` | string | yes | Audit routing |
| `initial` | RunInitialState | yes | Platform-neutral |
| `correlation_id` | string | no | Trace correlation |

## PlatformRunResponse

| Field | Type | When present |
|-------|------|--------------|
| `evidence` | PlatformEvidence | always |
| `result_type` | `run_state` \| `interrupt` \| `error` | always |
| `run_state` | RunState | success completion |
| `interrupt` | Interrupt | approval gate |
| `error` | error envelope | failure |

## PlatformEvidence

| Field | Type |
|-------|------|
| `tenant_id` | string |
| `caller_id` | string |
| `correlation_id` | string \| null |
| `subsystem_version` | string |

## Handshake Example

```python
from groundseal.adapter import PlatformAdapter, PlatformRunRequest
from groundseal.models import RunInitialState
from groundseal.runtime import Runtime

adapter = PlatformAdapter(Runtime())
resp = adapter.start_run(
    PlatformRunRequest(
        tenant_id="acme-corp",
        caller_id="orchestrator-svc",
        correlation_id="req-42",
        initial=RunInitialState(
            workflow_id="fixture_approval_v1",
            context={"branch_key": "a"},
        ),
    )
)
if resp.result_type == "interrupt":
    # parent platform routes to human approval UI
    ...
```

## Boundary Rules

1. Adapter validates adapter-local fields before delegating to runtime.
2. Runtime errors are wrapped, not swallowed.
3. `tenant_id` must never appear in `RunState.context` values.
4. Subsystem invariants cannot be disabled by adapter callers.

## Approver Authorization (v0.3.0)

Optional `ApproverValidator` on `PlatformAdapter` validates `approver_id` against tenant policy **before** resume when `approval.approved` is true.

| Implementation | Use case |
|----------------|----------|
| `AllowListApproverValidator` | Tests and simple allow-lists |
| `CallableApproverValidator` | Parent-platform IdP callback |

Unauthorized approvers return `result_type="error"` with code `APPROVER_UNAUTHORIZED`. Denied approvals (`approved=false`) skip validator and follow runtime denial policy.

```python
from groundseal.adapter import AllowListApproverValidator, PlatformAdapter

adapter = PlatformAdapter(
    Runtime(),
    approver_validator=AllowListApproverValidator({"reviewer-a", "reviewer-b"}),
)
```

Implementation: `groundseal/adapter/auth.py`
