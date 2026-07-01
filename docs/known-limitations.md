# Known Limitations

Honest scope boundaries after Phase 6.

## Workflow

- Only one hardcoded workflow: `fixture_approval_v1` (linear 2-node: `node_prepare` → `node_execute`).
- No generic DAG, dynamic graph loading, or parallel node execution.

## Storage

- `FileStorage` provides JSON file persistence without concurrent writer locking or transactions.
- No migration between storage schema versions.
- No encryption at rest.

## Patch Model

- Only `context.*` paths are patchable; full JSON Patch / arbitrary RunState paths are not supported.
- Optimistic concurrency via `target_version` only; no merge strategies.

## Approval

- Single approval gate on `node_execute`; no multi-step approval chains.
- Approval is a boolean + approver_id; adapter does not verify authZ with external IdP.

## Branching

- One deterministic branch decision at Run start from `context.branch_key`.
- No conditional edges between arbitrary nodes.

## Identity and Tenancy

- `PlatformAdapter` validates presence of `tenant_id` / `caller_id` but does not enforce platform authZ.
- Tenant must not leak into RunState; no cross-tenant isolation in core storage paths.

## Diagnostics

- Structured errors and eval JSON reports only; no operator UI (Phase 7).

## Testing

- 51+ pytest cases and 7 eval scenarios; production load and concurrency untested.

## What Phases 2–9 Prove

- Typed contracts, invariants, and fail-closed error paths.
- `run → interrupt → resume` offline and across runtime restart (FileStorage).
- Parent platform integration via thin adapter boundary.
- Evaluation baseline ratchet distinguishes regression from improvement.
- Operator-readable diagnostics without custom UI.
- Evidence-backed policy choices (storage default, denial policy).

## Post-Roadmap Gaps
