# Failure Taxonomy (Phase 3)

Machine-readable failure codes and regression fixture mapping.

## Error Codes

| Code | Phase | Meaning | Fail closed |
|------|-------|---------|-------------|
| `INVALID_INITIAL_STATE` | 3 | Malformed run input | yes |
| `INVALID_RESUME_INPUT` | 3 | Malformed resume input | yes |
| `INVALID_ADAPTER_REQUEST` | 5 | Missing adapter-local fields | yes |
| `WORKFLOW_NOT_FOUND` | 2 | Unknown workflow_id | yes |
| `RUN_NOT_FOUND` | 3 | Unknown run_id | yes |
| `RUN_TERMINAL` | 2 | Operation on terminal run | yes |
| `RUN_NOT_INTERRUPTED` | 2 | Resume on non-interrupted run | yes |
| `APPROVAL_DENIED` | 2 | Approval rejected | yes |
| `STALE_CHECKPOINT` | 2 | Checkpoint invalid or outdated | yes |
| `CHECKPOINT_RUN_MISMATCH` | 2 | Checkpoint/run_id mismatch | yes |
| `VERSION_MISMATCH` | 2 | Patch concurrency conflict | yes |
| `INVALID_PATCH` | 2 | Disallowed or malformed patch | yes |
| `DUPLICATE_PATCH` | 3 | Patch replay on same run | yes |
| `PATCH_ON_TERMINAL` | 2 | Patch on terminal state | yes |
| `INVARIANT_VIOLATION` | 1 | Invariant check failed | yes |
| `CHECKPOINT_NOT_FOUND` | 3 | Checkpoint ID not found | yes |
| `STORAGE_CORRUPT` | polish | Corrupt persisted JSON | yes |
| `INVALID_STORAGE_ID` | polish | Unsafe storage identifier | yes |

## Regression Fixtures

| Failure bucket | Fixture / test |
|----------------|----------------|
| invalid patch | `tests/fixtures/failures/patch_*.json`, `tests/test_failure_paths.py` |
| malformed resume | `tests/test_failure_paths.py::TestMalformedResume` |
| terminal resume | `tests/test_failure_paths.py::test_resume_completed_run_rejected` |
| duplicate patch | `tests/test_failure_paths.py::test_duplicate_patch_rejected` |
| adapter boundary | `tests/test_integration_boundary.py` |

## Observable Signals

Each code maps to `GroundSealError.to_dict()` with `code`, `message`, and `details`.

See [failure-analysis-plan.md](failure-analysis-plan.md) for investigation process.
