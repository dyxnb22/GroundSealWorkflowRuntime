# Code Review Notes (Polish Pass)

Summary of improvements applied after full codebase review.

## Security & Trust Boundaries

- **Approval bypass closed**: reserved context keys (`_approval_granted`, `approver_id`, `_*`) rejected in `validate_run_initial`.
- **Patch hardening**: cannot patch reserved `context._*` keys via `apply_patch`.
- **Adapter**: rejects `tenant_id` in initial context keys/values before run.
- **FileStorage**: ID sanitization, path escape checks, atomic writes, corrupt file → `STORAGE_CORRUPT`.

## Architecture

- Split `groundseal/runtime/` into `engine`, `patching`, `checkpointing`, `branching`, `fixture`, `timeutil`.
- Module-level `run()` / `resume()` wrappers match contract docs.
- `RunReader` protocol decouples diagnostics from concrete runtime.
- `Runtime.persist_run()` replaces direct `_storage` access in tests/eval.

## API Consistency

- `CHECKPOINT_NOT_FOUND` distinct from `STALE_CHECKPOINT`.
- `NODE_NOT_FOUND` on resume with invalid checkpoint node.
- `ApprovalDenialPolicy` documented; default remains `FAIL_RUN`.
- `PlatformRunResponse.result_type` typed as `Literal`.
- `resume_run(..., include_diagnostic=True)` parity with `start_run`.

## Tests (51 → 70)

- Approval bypass rejection, checkpoint run mismatch, unknown node resume.
- Resume without explicit checkpoint_id, REMAIN_INTERRUPTED policy.
- Reserved patch path, corrupt FileStorage load, tenant leak cases.
- Eval baseline ratchet compares per-scenario outcomes.

## Remaining Known Gaps

- No concurrent FileStorage locking (documented in TASKS.md).
- `apply_patch` free function still lacks duplicate tracking (use `Runtime.apply_patch`).
- Single fixture workflow only.
