# Patch Model Contract

## Purpose

Define atomic state mutations and apply semantics.

## Patch Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `patch_id` | string (UUID) | yes | Unique patch identifier |
| `target_version` | integer | yes | Expected `state_version` before apply (optimistic concurrency) |
| `operations` | list[PatchOperation] | yes | Ordered operations (applied atomically) |

## PatchOperation

| Field | Type | Required |
|-------|------|----------|
| `op` | enum | yes | `set`, `delete` |
| `path` | string | yes | Dot-path into RunState (e.g., `context.approval_token`) |
| `value` | any | set only | New value for `set` |

## Apply Rules (`apply_patch(state, patch) -> state`)

1. Reject if Run `status` is terminal → `PATCH_ON_TERMINAL`.
2. Reject if `patch.target_version != state.state_version` → `VERSION_MISMATCH`.
3. Validate each operation path is allowed (whitelist in Phase 2: `context.*` only).
4. Apply all operations atomically; on any failure, no partial apply.
5. Increment `state_version` by 1 and update `updated_at`.

## Conflict Strategy

- Optimistic concurrency via `target_version`; no silent merge.
- Duplicate `patch_id` on same Run → `DUPLICATE_PATCH`.

## Non-Goals (Phase 2)

- JSON Patch full RFC compliance for all paths.
- Patch replay across different Runs.
