# RunState Contract

## Purpose

Define the authoritative runtime state schema for a single Run.

## Schema (conceptual)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `run_id` | string (UUID) | yes | Unique Run identifier |
| `state_version` | integer ≥ 0 | yes | Monotonic version; increments on every state mutation |
| `status` | enum | yes | `pending`, `running`, `interrupted`, `completed`, `failed`, `cancelled` |
| `current_node_id` | string \| null | yes | Active or next node; null when terminal |
| `node_results` | map[node_id → NodeResult] | yes | Completed or failed node outputs |
| `branch_decisions` | list[BranchDecision] | yes | Ordered record of deterministic branch choices |
| `context` | object | yes | Workflow-local key-value bag (typed keys in fixtures) |
| `created_at` | ISO8601 string | yes | Run creation timestamp (deterministic in tests via injection) |
| `updated_at` | ISO8601 string | yes | Last mutation timestamp |

## NodeResult

| Field | Type | Required |
|-------|------|----------|
| `node_id` | string | yes |
| `status` | `completed` \| `failed` | yes |
| `output` | object | yes |
| `completed_at` | ISO8601 string | yes |

## BranchDecision

| Field | Type | Required |
|-------|------|----------|
| `decision_id` | string | yes |
| `inputs_hash` | string | yes | Deterministic hash of branch inputs |
| `selected_edge` | string | yes |

## Ownership

- The runtime owns mutation of RunState.
- External callers receive copies; mutations flow through `apply_patch` or runtime node execution only.

## Versioning Rules

1. Initial `state_version` is `0` at Run creation.
2. Each successful patch or node completion increments `state_version` by exactly 1.
3. Checkpoints record the `state_version` at emission time.

## Validation

- `status` must be consistent with `current_node_id` (terminal → `current_node_id` must be null).
- `node_results` keys must not duplicate.
- Unknown fields in strict mode are rejected (fail closed).

## Non-Goals (Phase 2)

- Multi-tenant isolation fields (adapter-local).
- Arbitrary nested graph definitions (hardcoded fixture workflow only).
