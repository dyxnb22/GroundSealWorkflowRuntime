# Experiment: Approval Denial Policy (Phase 8)

## Hypothesis

`FAIL_RUN` closes the run on denial (audit-clear terminal state); `REMAIN_INTERRUPTED` allows operator retry without starting a new run.

## Setup

- Two `Runtime` instances with `denial_policy=FAIL_RUN` vs `REMAIN_INTERRUPTED`.
- Deny first resume attempt; observe status; attempt approved retry.

## Observations

| Policy | Status after deny | Can retry resume | Error code |
|--------|-------------------|------------------|------------|
| fail_run | failed | no | APPROVAL_DENIED |
| remain_interrupted | interrupted | yes | APPROVAL_DENIED |

## Tradeoffs

| | FAIL_RUN | REMAIN_INTERRUPTED |
|---|----------|-------------------|
| Audit clarity | explicit terminal failure | run stays open |
| Operator UX | must start new run | can re-submit approval |
| Risk | lower ambiguity | run may linger |

## Conclusion

**Default**: `FAIL_RUN` — aligns with fail-closed design and clear terminal semantics.

**Optional**: `REMAIN_INTERRUPTED` for platforms with in-loop approval UI where denial is non-terminal.

Configure via `Runtime(denial_policy=ApprovalDenialPolicy.REMAIN_INTERRUPTED)`.

See [decision-memo.md](decision-memo.md).
