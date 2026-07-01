# Roadmap

## Phase 0: Framing And Contracts

- **Status**: complete
- Goal: define vocabulary, contracts, boundaries, and non-goals.
- Artifacts: [glossary.md](glossary.md), [contracts/](contracts/), updated evaluation and integration docs.
- Exit criteria: met — tasks map to phases; contracts guide implementation.

## Phase 1: Domain Model Baseline

- **Status**: complete
- Goal: define the minimal schemas and invariants for the subsystem.
- Artifacts: Pydantic models in `groundseal/models/`, [invariants.md](invariants.md), JSON fixtures in `tests/fixtures/`.
- Exit criteria: met — core types and invariants are reviewable; schema tests pass.

## Phase 2: Deterministic Core Slice

- **Status**: complete
- Goal: implement the smallest useful core behavior with no external dependency sprawl.
- Artifacts: `groundseal/runtime/`, 30 passing tests, [known-limitations.md](known-limitations.md).
- Exit criteria: met — `run → interrupt → resume` path works under deterministic offline tests.

## Phase 3: Failure Handling And Invariants

- **Status**: complete
- Goal: make error, denial, and malformed-input paths explicit.
- Artifacts: [failure-taxonomy.md](failure-taxonomy.md), [repair-notes.md](repair-notes.md), `tests/test_failure_paths.py`, `groundseal/validation/`.
- Exit criteria: met — high-risk paths fail closed with structured errors and regression tests.

## Phase 4: Evaluation Baseline

- **Status**: complete
- Goal: measure core quality and regressions.
- Artifacts: `groundseal/evaluation/`, [eval/baseline.json](../eval/baseline.json), `scripts/run_eval.py`, CI workflow, [evaluation-baseline-report.md](evaluation-baseline-report.md).
- Exit criteria: met — ratcheted baseline distinguishes improvement from regression.

## Phase 5: Integration Contract

- **Status**: complete
- Goal: define how parent systems call into GroundSealWorkflowRuntime.
- Artifacts: `groundseal/adapter/`, [contracts/adapter-contract.md](contracts/adapter-contract.md), `tests/test_integration_boundary.py`.
- Exit criteria: met — subsystem consumable via adapter without deep internal knowledge.

## Phase 6: Durable Or Multi-Run Behavior

- **Status**: complete (minimal file persistence)
- Goal: add persistence and multi-session resume where relevant.
- Artifacts: `groundseal/storage/`, [storage-contract.md](storage-contract.md), `tests/test_storage.py`.
- Exit criteria: met — interrupt/resume survives runtime restart with FileStorage.

## Phase 7: Operator And Reviewer Experience

- **Status**: complete
- Goal: improve legibility of outputs, diagnostics, or human review flow.
- Artifacts: `groundseal/diagnostics/`, [contracts/diagnostic-report.md](contracts/diagnostic-report.md), [review-ux-notes.md](review-ux-notes.md).
- Exit criteria: met — reviewers can inspect runs via summary, narrative, and hints without reading runtime code.

## Phase 8: Comparative Experiments

- **Status**: complete
- Goal: compare at least two meaningful approaches or policies.
- Artifacts: `groundseal/evaluation/experiments.py`, [experiments/](experiments/), `tests/test_experiments.py`.
- Exit criteria: met — storage backend and approval denial policies compared with evidence-backed conclusions.

## Phase 9: Case Study And Integration Backfeed

- **Status**: complete
- Goal: summarize what this project changed in the broader platform understanding.
- Artifacts: [case-study.md](case-study.md), [integration-recommendations.md](integration-recommendations.md).
- Exit criteria: met — external readers can understand build, lessons, and integration path.

