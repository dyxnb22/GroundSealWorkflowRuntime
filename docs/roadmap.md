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

- Goal: improve legibility of outputs, diagnostics, or human review flow.
- Why it matters: a subsystem that cannot be reviewed will not be trusted.
- Required artifacts: display models, report templates, review UX notes.
- Evaluation criteria: humans can inspect the subsystem without reverse-engineering it.
- Exit criteria: evidence and outcomes are understandable to non-authors.
- Common risks: polish replacing clarity, overbuilt UI before stable contracts.

## Phase 8: Comparative Experiments

- Goal: compare at least two meaningful approaches or policies.
- Why it matters: this is where judgment becomes visible.
- Required artifacts: experiment notes, observed tradeoffs, decision memo.
- Evaluation criteria: tradeoffs are evidence-backed rather than taste-driven.
- Exit criteria: the project demonstrates reasoning, not just implementation volume.
- Common risks: comparison without controls, no clear conclusion.

## Phase 9: Case Study And Integration Backfeed

- Goal: summarize what this project changed in the broader platform understanding.
- Why it matters: the subsystem should teach something reusable.
- Required artifacts: case study, integration recommendations, residual risks.
- Evaluation criteria: the subsystem is credible as a standalone project and a reusable layer.
- Exit criteria: external readers can understand both the build and the lessons.
- Common risks: retrospective storytelling unsupported by artifacts.
