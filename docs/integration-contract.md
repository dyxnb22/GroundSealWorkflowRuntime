# Integration Contract

## Role In A Larger System

GroundSealWorkflowRuntime plugs into a parent platform as a specialized subsystem rather than a hidden helper module. See [glossary.md](glossary.md) for platform-neutral vs adapter-local boundaries.

## Integration Expectations

- Callers provide typed input (`RunInitialState`, `ResumeInput`, `Patch`), not arbitrary prompts.
- Callers receive typed output (`RunState`, `Interrupt`, `Checkpoint`) plus structured errors.
- Subsystem invariants remain enforced even when the parent platform wants convenience.
- Failure states are explicit and machine-readable (see [contracts/public-api.md](contracts/public-api.md)).

## Adapter Layer (Phase 5)

Use `PlatformAdapter` for parent platform handshakes. See [contracts/adapter-contract.md](contracts/adapter-contract.md).

```python
from groundseal.adapter import PlatformAdapter, PlatformRunRequest
from groundseal.runtime import Runtime

adapter = PlatformAdapter(Runtime())
response = adapter.start_run(
    PlatformRunRequest(
        tenant_id="tenant-1",
        caller_id="workflow-orchestrator",
        initial=...,  # RunInitialState
    )
)
```

## Desired Boundary Shape

- thin adapter layer (`groundseal/adapter/`)
- explicit request and response schemas
- deterministic local mode for testing
- minimal assumptions about the rest of the platform

## Platform-Neutral Types (stable)

| Type | Contract doc |
|------|----------------|
| `RunState` | [run-state.md](contracts/run-state.md) |
| `Patch` | [patch-model.md](contracts/patch-model.md) |
| `Checkpoint` | [checkpoint.md](contracts/checkpoint.md) |
| `Interrupt` / `ResumeInput` | [interrupt-resume.md](contracts/interrupt-resume.md) |
| Public API | [public-api.md](contracts/public-api.md) |

## Adapter-Local Concerns (parent platform)

- tenancy and identity enforcement (`PlatformRunRequest.tenant_id`)
- external audit sink routing (`PlatformEvidence`)
- authZ for approval actions
- persistence backend selection — see [storage-contract.md](storage-contract.md)

## Boundary Tests

`tests/test_integration_boundary.py` verifies adapter wrapping, error surfacing, and tenant isolation.

## Questions To Resolve Later

- where tenancy and identity should be enforced in the adapter beyond presence checks
- how much evidence should flow back to the caller by default
