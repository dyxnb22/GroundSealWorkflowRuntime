# Case Study: GroundSealWorkflowRuntime

## Problem

Agent workflow runtimes often blur planning, execution, and side effects. Long-lived workflows need explicit pause/resume, auditable state, and deterministic evaluation — without inheriting an entire platform codebase.

## Approach

Build a **subsystem-first** runtime with:

1. Typed contracts before implementation (Phases 0–1)
2. Minimal deterministic core (`run → interrupt → resume`) (Phase 2)
3. Fail-closed edges and regression tests (Phase 3)
4. Ratcheted evaluation baseline (Phase 4)
5. Thin platform adapter (Phase 5)
6. Optional file persistence (Phase 6)
7. Operator diagnostics (Phase 7)
8. Evidence-backed design comparisons (Phase 8)

## What Was Built

| Artifact | Count / status |
|----------|----------------|
| Contract docs | 7+ under `docs/contracts/` |
| Python modules | models, runtime, storage, adapter, diagnostics, evaluation |
| Tests | 60+ pytest cases |
| Eval scenarios | 7 baseline + 2 experiment suites |

## Key Lessons

1. **Contract-first pays off** — Phase 0–1 docs prevented scope drift during implementation.
2. **Fail closed at boundaries** — validation layer caught empty approver_id and duplicate patches before silent corruption.
3. **Storage abstraction early** — enabled Phase 6 restart tests without rewriting runtime logic.
4. **Diagnostics are not UI** — `RunSummary` + narrative text give reviewers enough context without a dashboard.
5. **Experiments need controls** — comparing storage backends and denial policies produced concrete defaults, not taste calls.

## Evidence

- All pytest and eval baseline tests pass locally.
- Phase 8 experiments documented with reproducible runners in `groundseal/evaluation/experiments.py`.
- Known limitations honestly scoped in [known-limitations.md](../known-limitations.md).

## Residual Risks

- Single hardcoded workflow; generalization untested.
- No concurrent writer support on FileStorage.
- Adapter authZ is presence-only, not integrated with external IdP.

See [integration-recommendations.md](integration-recommendations.md) for backfeed guidance.
