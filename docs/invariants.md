# Invariants

Rules that must always hold in GroundSealWorkflowRuntime. Enforced in `groundseal/invariants/` and after every state mutation in the runtime.

## RunState Invariants

| ID | Rule | Violation code |
|----|------|----------------|
| RS-1 | Terminal status (`completed`, `failed`, `cancelled`) implies `current_node_id is None` | `INVARIANT_VIOLATION` |
| RS-2 | `interrupted` status implies `current_node_id` is set | `INVARIANT_VIOLATION` |
| RS-3 | `node_results` dict keys match `NodeResult.node_id` | `INVARIANT_VIOLATION` |
| RS-4 | `state_version >= 0` and increments by exactly 1 per mutation | enforced at mutation sites |
| RS-5 | No patch or node execution permitted when terminal | `PATCH_ON_TERMINAL`, `RUN_TERMINAL` |

## Checkpoint Invariants

| ID | Rule | Violation code |
|----|------|----------------|
| CP-1 | `checkpoint.run_id == state_snapshot.run_id` | `CHECKPOINT_RUN_MISMATCH` |
| CP-2 | `checkpoint.state_version == state_snapshot.state_version` | `INVARIANT_VIOLATION` |
| CP-3 | Embedded snapshot satisfies RunState invariants | `INVARIANT_VIOLATION` |

## Patch Invariants

| ID | Rule | Violation code |
|----|------|----------------|
| PA-1 | `patch.target_version == state.state_version` at apply time | `VERSION_MISMATCH` |
| PA-2 | Only `context.*` paths allowed in Phase 2 | `INVALID_PATCH` |
| PA-3 | Apply is atomic (all ops or none) | `INVALID_PATCH` |
| PA-4 | Duplicate `patch_id` per run rejected | `DUPLICATE_PATCH` |

## Branch Invariants

| ID | Rule | Violation code |
|----|------|----------------|
| BR-1 | Same serialized context → same `inputs_hash` and `selected_edge` | test assertion |
| BR-2 | Branch decisions append-only within a Run | enforced by runtime |

## Resume Invariants

| ID | Rule | Violation code |
|----|------|----------------|
| RE-1 | Resume only when `status == interrupted` | `RUN_NOT_INTERRUPTED` |
| RE-2 | Checkpoint version must not be older than current state | `STALE_CHECKPOINT` |
| RE-3 | Denied approval: default `FAIL_RUN` → `failed`; optional `REMAIN_INTERRUPTED` keeps `interrupted` | `APPROVAL_DENIED` |
