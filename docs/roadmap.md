# Roadmap

## Phase 0: Framing And Contracts

- Goal: define vocabulary, contracts, boundaries, and non-goals.
- Why it matters: without this, later implementation quality is mostly luck.
- Required artifacts: README, brief, architecture, roadmap, evaluation plan.
- Evaluation criteria: docs are specific enough to guide a new agent with minimal clarification.
- Exit criteria: future tasks map to explicit phases without ambiguity.
- Common risks: vague scope, hidden coupling, premature implementation.

## Phase 1: Domain Model Baseline

- Goal: define the minimal schemas and invariants for the subsystem.
- Why it matters: implementation quality depends on model clarity.
- Required artifacts: schema docs, validation notes, example payloads.
- Evaluation criteria: reviewers can explain the core types and state transitions.
- Exit criteria: core types and invariants are reviewable and stable enough for a first implementation slice.
- Common risks: ad-hoc types, ambiguous ownership, hidden state transitions.

## Phase 2: Deterministic Core Slice

- Goal: implement the smallest useful core behavior with no external dependency sprawl.
- Why it matters: proves the project can move from paper to executable form.
- Required artifacts: minimal implementation, unit tests, known limitations.
- Evaluation criteria: one narrow path works and is testable offline.
- Exit criteria: the subsystem performs one meaningful end-to-end behavior under deterministic tests.
- Common risks: overbuilding, confusing prototype code with production direction.

## Phase 3: Failure Handling And Invariants

- Goal: make error, denial, and malformed-input paths explicit.
- Why it matters: safety and reliability are mostly decided at the edges.
- Required artifacts: failure taxonomy, negative tests, repair notes.
- Evaluation criteria: major high-risk failure paths are observable and fail predictably.
- Exit criteria: unsafe or unclear paths fail closed instead of degrading silently.
- Common risks: happy-path bias, fallback paths with unclear semantics.

## Phase 4: Evaluation Baseline

- Goal: measure core quality and regressions.
- Why it matters: otherwise improvement claims are anecdotal.
- Required artifacts: fixture suites, metrics, dashboard draft.
- Evaluation criteria: at least one ratcheted evaluation path exists.
- Exit criteria: the project can distinguish improvement from accidental change.
- Common risks: weak metrics, uninformative fixtures, baselines without explanations.

## Phase 5: Integration Contract

- Goal: define how parent systems call into GroundSealWorkflowRuntime.
- Why it matters: a subsystem is only reusable when its boundary is explicit.
- Required artifacts: adapter contract, input/output examples, boundary tests.
- Evaluation criteria: integration assumptions are small and explicit.
- Exit criteria: the subsystem can be consumed without deep internal knowledge.
- Common risks: leaky abstractions, caller-driven invariant weakening.

## Phase 6: Durable Or Multi-Run Behavior

- Goal: add persistence, replay, lifecycle, or multi-step behavior where relevant.
- Why it matters: many subsystem failures only appear after the first run.
- Required artifacts: storage notes, lifecycle model, migration concerns.
- Evaluation criteria: longer-lived behavior does not break earlier guarantees.
- Exit criteria: repeatable or durable behavior is intentionally designed, not accidental.
- Common risks: hidden state, replay drift, migration shortcuts.

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
