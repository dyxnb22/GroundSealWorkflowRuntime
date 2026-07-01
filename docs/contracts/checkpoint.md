# Checkpoint Contract

## Purpose

Define immutable snapshots for interrupt/resume and audit.

## Checkpoint Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `checkpoint_id` | string (UUID) | yes | Unique checkpoint identifier |
| `run_id` | string (UUID) | yes | Owning Run |
| `state_version` | integer | yes | RunState version at emission |
| `state_snapshot` | RunState | yes | Full authoritative snapshot |
| `reason` | enum | yes | `scheduled`, `approval_required`, `manual` |
| `emitted_at` | ISO8601 string | yes | Emission timestamp |

## Semantics (`emit_checkpoint(state) -> Checkpoint`)

1. Validates current RunState against invariants before emission.
2. Produces a deep copy of state; subsequent mutations do not alter stored checkpoint.
3. Assigns new `checkpoint_id`; checkpoints are append-only per Run.
4. Returns the Checkpoint record to caller/runtime store.

## Storage (Phase 2)

- In-memory dict keyed by `checkpoint_id`; secondary index by `run_id` (latest wins for resume unless specified).
- No persistence durability guarantees in Phase 2.

## Resume Selection

- Default: latest checkpoint for `run_id` with matching or lower `state_version` than resume request expects.
- Stale checkpoint resume (version older than current run state) → `STALE_CHECKPOINT`.

## Fail Closed

- Emit on terminal state → allowed for audit but resume from terminal → `RUN_TERMINAL`.
- Missing run_id in snapshot vs argument → `CHECKPOINT_RUN_MISMATCH`.
