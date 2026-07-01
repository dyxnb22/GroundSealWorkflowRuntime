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
