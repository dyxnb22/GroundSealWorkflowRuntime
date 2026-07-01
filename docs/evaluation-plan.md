# Evaluation Plan

## Purpose

Define how this project will be judged as it evolves.

## Evaluation Goals

- Verify contract correctness.
- Catch regressions early.
- Expose failure patterns instead of hiding them in aggregate scores.
- Produce evidence useful to reviewers and future maintainers.

## Evaluation Layers

1. Schema and contract validation.
2. Deterministic unit tests for core logic.
3. Fixture-based scenario tests.
4. Negative and adversarial tests.
5. Integration-boundary tests.

## Metrics To Track

- Contract pass rate.
- Negative-path correctness.
- Regression count.
- Explainability coverage.
- Unresolved known-risk count.

## Reporting Expectations

Every evaluation run should leave behind:
- what changed
- what was measured
- what regressed or improved
- what is still not covered

## Ratchet Policy

Baselines should move only when the team can explain why the new result is better or when a prior baseline was shown to be wrong.

## Case Categories (Phase 2 baseline)

Each category maps to at least one deterministic fixture under `tests/fixtures/`.

| Category | Hypothesis | Primary assertion |
|----------|------------|-------------------|
| `happy_path_run_complete` | Linear workflow completes without interrupt | Final `status` is `completed`; all nodes in `node_results` |
| `interrupt_at_approval_then_resume` | Approval gate pauses and resume continues | First `run` returns `Interrupt`; `resume` yields `completed` |
| `invalid_patch_rejected` | Bad patches fail closed | `apply_patch` raises structured error; state unchanged |
| `resume_from_stale_checkpoint` | Stale checkpoint rejected | `resume` raises `STALE_CHECKPOINT` |
| `branch_determinism_same_input` | Same branch inputs → same edge | Repeated branch evaluation yields identical `selected_edge` |

## Fixture Naming

- Positive: `tests/fixtures/<category>/valid.json`
- Negative: `tests/fixtures/<category>/invalid.json` (where applicable)

## Phase 2 Exit Metrics

- All five categories have passing tests.
- Zero unexplained test flakiness across three consecutive local runs.
