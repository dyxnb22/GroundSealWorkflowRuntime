# Interrupt and Resume Contract

## Purpose

Define approval interruption and resume semantics.

## Interrupt

An interrupt occurs when:

1. A node with `requires_approval: true` is reached, or
2. Policy explicitly requests halt (Phase 2: approval path only).

### Interrupt Record

| Field | Type | Required |
|-------|------|----------|
| `run_id` | string | yes |
| `checkpoint_id` | string | yes |
| `reason` | `approval_required` | yes |
| `node_id` | string | yes |
| `message` | string | yes |

### Interrupt Behavior

1. Set Run `status` to `interrupted`.
2. Set node status to `interrupted`.
3. Call `emit_checkpoint(state)` with `reason: approval_required`.
4. Return Interrupt record to caller (not final state).

## Resume (`resume(run_id, resume_input) -> state`)

### ResumeInput

| Field | Type | Required |
|-------|------|----------|
| `run_id` | string | yes |
| `checkpoint_id` | string | no | Defaults to latest for run |
| `approval` | object | yes |
| `approval.approved` | boolean | yes |
| `approval.approver_id` | string | yes |

### Resume Rules

1. Reject if Run is not `interrupted` → `RUN_NOT_INTERRUPTED`.
2. Reject if `approval.approved` is false → `APPROVAL_DENIED`. Default policy (`FAIL_RUN`) sets Run → `failed`; optional `REMAIN_INTERRUPTED` keeps Run `interrupted`.
3. Load checkpoint; reject if missing → `CHECKPOINT_NOT_FOUND`; stale → `STALE_CHECKPOINT`; wrong run → `CHECKPOINT_RUN_MISMATCH`.
4. Apply approval token to context via internal patch (increments version).
5. Continue node execution from interrupted node; on success proceed to next fixture node.
6. Return updated RunState (may be terminal or interrupted again).

## Approval Fail Closed

- Missing approval fields → `INVALID_RESUME_INPUT`.
- Resume on completed/failed/cancelled Run → `RUN_TERMINAL`.
