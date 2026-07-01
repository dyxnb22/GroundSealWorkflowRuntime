# Failure Analysis Plan

## Purpose

This document defines how GroundSealWorkflowRuntime should study failures instead of merely routing around them.

## Failure Categories

| Category | Description | Observable signal |
|----------|-------------|-------------------|
| resume inconsistency | Resume produces state divergent from checkpoint + approval | `error.code == STALE_CHECKPOINT` or `state_version` mismatch after resume; test assertion on `node_results` |
| implicit state mutation | State changes without patch or node execution | Invariant check failure; unexpected `state_version` increment |
| branch drift between runtimes | Same inputs yield different branch edges | `branch_decisions[-1].selected_edge` differs across runs; `BRANCH_DRIFT` in diagnostics |
| terminal-state ambiguity | Operations accepted on terminal Run | `error.code` in `PATCH_ON_TERMINAL`, `RUN_TERMINAL`, `RUN_NOT_INTERRUPTED` |
| version mismatch | Optimistic concurrency violated | `error.code == VERSION_MISMATCH`; `details.expected_version` field |
| approval denied | Resume rejected without continuing | `error.code == APPROVAL_DENIED`; Run `status == failed` |
| invalid patch | Malformed or disallowed patch | `error.code == INVALID_PATCH`; state deep-equal to pre-call |

## Required Failure Record

Each meaningful failure investigation should capture:
- the triggering input or condition
- the expected behavior
- the observed behavior
- the most likely root cause
- whether the issue is deterministic or intermittent
- what test or guard should prevent recurrence

## Review Cadence

- Review new failures before expanding scope.
- Promote repeated issues into explicit regression tests.
- Update docs when a failure changes the architecture or contract story.

## Anti-Patterns

- Closing failures with vague "needs more work" notes.
- Treating unexplained regressions as acceptable churn.
- Fixing symptoms while leaving contract ambiguity in place.

## Mapping to Evaluation Categories

| Eval category | Primary failure buckets |
|---------------|-------------------------|
| `happy_path_run_complete` | terminal-state ambiguity (negative control) |
| `interrupt_at_approval_then_resume` | resume inconsistency |
| `invalid_patch_rejected` | invalid patch, version mismatch |
| `resume_from_stale_checkpoint` | resume inconsistency, stale checkpoint |
| `branch_determinism_same_input` | branch drift |
