# Known Limitations (Phase 2)

Honest scope boundaries for the current implementation slice.

## Workflow

- Only one hardcoded workflow: `fixture_approval_v1` (linear 2-node: `node_prepare` → `node_execute`).
- No generic DAG, dynamic graph loading, or parallel node execution.

## Storage

- Checkpoints and runs live in process memory only; no durability across restarts.
- No migration or replay from external storage.

## Patch Model

- Only `context.*` paths are patchable; full JSON Patch / arbitrary RunState paths are not supported.
- Optimistic concurrency via `target_version` only; no merge strategies.

## Approval

- Single approval gate on `node_execute`; no multi-step approval chains.
- Approval is a boolean + approver_id; no signature or external auth integration.

## Branching

- One deterministic branch decision at Run start from `context.branch_key`.
- No conditional edges between arbitrary nodes.

## Identity and Tenancy

- No tenancy, authZ, or adapter-layer routing (deferred to Phase 5 integration).

## Diagnostics

- Structured errors only; no operator UI or report templates (Phase 7).

## Testing

- Fixed clock injection for timestamps; production wall-clock behavior untested.
- Five evaluation categories covered; adversarial and integration-boundary suites deferred to Phase 3–4.

## What Phase 2 Proves

- Typed contracts parse and validate.
- Invariants enforce fail-closed semantics.
- `run → interrupt → resume` works offline with deterministic tests.
- Patches and checkpoints behave per contract docs.
