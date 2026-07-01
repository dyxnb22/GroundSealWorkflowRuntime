# Known Limitations

Honest scope boundaries after v0.3.0 baseline closure.

## Workflow

- **Linear node lists only** — workflows are ordered sequences, not DAGs.
- Graphs load from JSON via `WorkflowRegistry` (`workflows/*.json`); built-in default remains `fixture_approval_v1`.
- Handlers are fixture handlers (`prepare`, `execute`); no arbitrary side-effect executors.
- No parallel node execution or dynamic graph mutation at runtime.

## Storage

- `FileStorage` v2: JSON files, per-run `fcntl` locks, v1→v2 migration on init.
- Non-blocking lock acquire only; no retry/backoff policy (`STORAGE_LOCK_TIMEOUT` on contention).
- No transactions across runs; no encryption at rest.
- No cross-tenant path isolation in core storage (tenant is adapter-local).

## Patch Model

- Only `context.*` paths are patchable; full JSON Patch / arbitrary RunState paths are not supported.
- Optimistic concurrency via `target_version` only; no merge strategies.

## Approval

- Single approval gate per node (`requires_approval`); no multi-step approval chains.
- Optional `ApproverValidator` on adapter validates `approver_id` when `approved=true`; parent must inject policy (allow-list or IdP callback).
- Denied approvals follow runtime `ApprovalDenialPolicy`; validator is not invoked.

## Branching

- One deterministic branch decision at run start from `context.branch_key`.
- No conditional edges between arbitrary nodes.

## Identity and Tenancy

- `PlatformAdapter` validates presence of `tenant_id` / `caller_id` and blocks tenant leakage into `RunState`.
- No platform-wide authZ beyond optional approver validation hook.
- Tenant must not appear in RunState; storage does not partition by tenant.

## Diagnostics

- Structured errors, eval JSON reports, and `DiagnosticReport` summaries; no operator UI.

## Testing

- **88** pytest cases and **7** eval baseline scenarios; production load and multi-writer stress untested.

## What Phases 0–9 + v0.3.0 Prove

- Typed contracts, invariants, and fail-closed error paths.
- `run → interrupt → resume` offline and across runtime restart (FileStorage).
- Parent platform integration via thin adapter boundary with optional approver auth.
- JSON workflow loading beyond a single hardcoded graph.
- Evaluation baseline ratchet distinguishes regression from improvement.
- Operator-readable diagnostics without custom UI.
- Evidence-backed policy choices (storage default, denial policy).

## Post-Baseline Work (TASKS Now)

- DAG workflow graphs.
- FileStorage lock retry/backoff policy.
- Cross-tenant storage isolation in FileStorage paths.
