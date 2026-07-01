# Public API Contract

## Purpose

Define the narrow public surface for GroundSealWorkflowRuntime.

## Functions

### `run(initial_state) -> RunState | Interrupt`

Prefer `Runtime.run()` or the module wrapper `groundseal.run()`:

```python
from groundseal import Runtime, RunInitialState, run

rt = Runtime()
outcome = rt.run(RunInitialState(workflow_id="fixture_approval_v1", context={}))
# or: outcome = run(RunInitialState(...))
```

**Input**: `RunInitialState`

| Field | Type | Required |
|-------|------|----------|
| `workflow_id` | string | yes |
| `context` | object | yes |
| `run_id` | string | no | Generated if omitted |

**Output**:

- `RunState` if workflow completes without interrupt, or
- `Interrupt` if approval is required (Run remains resumable).

**Errors**: `INVALID_INITIAL_STATE`, `WORKFLOW_NOT_FOUND`

Workflow definitions are resolved via `WorkflowRegistry` (see [workflow-definition.md](workflow-definition.md)). Default registry includes `fixture_approval_v1`; additional graphs load from JSON at startup.

---

### `resume(run_id, resume_input) -> RunState | Interrupt`

See [interrupt-resume.md](interrupt-resume.md).

**Errors**: `RUN_NOT_FOUND`, `RUN_NOT_INTERRUPTED`, `RUN_TERMINAL`, `INVALID_RESUME_INPUT`, `APPROVAL_DENIED`, `CHECKPOINT_NOT_FOUND`, `STALE_CHECKPOINT`, `CHECKPOINT_RUN_MISMATCH`, `NODE_NOT_FOUND`

---

### `apply_patch(state, patch) -> RunState`

See [patch-model.md](patch-model.md).

**Errors**: `PATCH_ON_TERMINAL`, `VERSION_MISMATCH`, `INVALID_PATCH`, `DUPLICATE_PATCH`

---

### `emit_checkpoint(state) -> Checkpoint`

See [checkpoint.md](checkpoint.md).

**Errors**: `INVARIANT_VIOLATION`, `CHECKPOINT_RUN_MISMATCH`

## Error Envelope

All errors return a structured object:

```json
{
  "code": "VERSION_MISMATCH",
  "message": "human-readable summary",
  "details": {}
}
```

## Trust Boundary

- All inputs are untrusted; validate before mutation.
- Callers cannot disable invariant checks or skip version checks.

## Platform-Neutral Surface

These types and error codes are stable integration contracts. Tenancy, auth, and external audit routing are adapter-local concerns.
