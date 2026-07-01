# Public API Contract

## Purpose

Define the narrow public surface for GroundSealWorkflowRuntime.

## Functions

### `run(initial_state) -> RunState | Interrupt`

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

---

### `resume(run_id, resume_input) -> RunState | Interrupt`

See [interrupt-resume.md](interrupt-resume.md).

**Errors**: `RUN_NOT_FOUND`, `RUN_NOT_INTERRUPTED`, `RUN_TERMINAL`, `INVALID_RESUME_INPUT`, `APPROVAL_DENIED`, `STALE_CHECKPOINT`

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
