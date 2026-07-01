# Repair Notes (Phase 3)

Documented failure clusters and guards added during Phase 3.

## RN-001: Resume on completed run error code ambiguity

- **Trigger**: `resume()` called after successful `run()` without interrupt.
- **Expected**: Fail closed; no state mutation.
- **Observed**: `RUN_TERMINAL` (completed is terminal).
- **Root cause**: Terminal check runs before interrupted check.
- **Deterministic**: yes
- **Guard**: `tests/test_failure_paths.py::test_resume_completed_run_rejected`; eval scenario accepts `RUN_TERMINAL` or `RUN_NOT_INTERRUPTED`.

## RN-002: Empty approver_id passed schema validation

- **Trigger**: `ResumeInput` with `approver_id=""`.
- **Expected**: Reject before runtime mutation.
- **Observed**: Previously accepted; could proceed with blank audit trail.
- **Root cause**: Pydantic `str` allows empty string; no boundary validator.
- **Deterministic**: yes
- **Guard**: `groundseal/validation.validate_resume_input`; `INVALID_RESUME_INPUT`.

## RN-003: Duplicate patch replay

- **Trigger**: Same `patch_id` applied twice on one run.
- **Expected**: Second apply rejected.
- **Observed**: Phase 2 tracked patches in runtime dict only; not durable.
- **Root cause**: Patch tracking not in storage abstraction.
- **Deterministic**: yes
- **Guard**: Storage-backed `has_applied_patch` / `mark_patch_applied`; `DUPLICATE_PATCH` test.

## RN-004: Adapter tenant leakage risk

- **Trigger**: Parent passes `tenant_id` that could be copied into `RunState.context`.
- **Expected**: Tenant stays adapter-local.
- **Observed**: No guard in Phase 2.
- **Root cause**: Missing boundary assertion.
- **Deterministic**: yes
- **Guard**: `PlatformAdapter._assert_no_tenant_leak`; integration tests.
