# Decision Memo: Phase 8 Experiments

## Decisions

### D-001: Default storage backend

- **Chosen**: MemoryStorage for tests and ephemeral runs.
- **Alternative considered**: FileStorage as default.
- **Why**: Tests stay fast and dependency-free; FileStorage opt-in for durability scenarios.
- **Evidence**: [storage-backend-comparison.md](storage-backend-comparison.md), `tests/test_experiments.py`.

### D-002: Approval denial policy

- **Chosen**: `ApprovalDenialPolicy.FAIL_RUN` as default.
- **Alternative considered**: `REMAIN_INTERRUPTED`.
- **Why**: Terminal failure is easier to audit and matches fail-closed posture; retry-without-new-run is opt-in.
- **Evidence**: [approval-policy-comparison.md](approval-policy-comparison.md).

## Residual Uncertainty

- FileStorage concurrency under parallel writers (deferred to Later in TASKS.md).
- Whether parent platforms prefer diagnostic JSON vs plain text by default.

## Revisit Triggers

- Production incident involving stale interrupted runs lingering under REMAIN_INTERRUPTED.
- Requirement for cross-region checkpoint replication (outside current scope).
