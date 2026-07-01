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
9. Case study and integration backfeed (Phase 9)
10. Post-review hardening and v0.3.0 baseline (locking, migration, workflow registry, approver auth)

## What Was Built

| Artifact | Count / status |
|----------|----------------|
| Contract docs | 8+ under `docs/contracts/` |
| Python modules | models, runtime, storage, adapter, workflow, diagnostics, evaluation |
| Tests | **88** pytest cases |
| Eval scenarios | 7 baseline + 2 experiment suites |
| Version | **0.3.0** subsystem baseline |

## Key Lessons

1. **Contract-first pays off** — Phase 0–1 docs prevented scope drift during implementation.
2. **Fail closed at boundaries** — validation layer caught empty approver_id, reserved context keys, and duplicate patches before silent corruption.
3. **Storage abstraction early** — enabled Phase 6 restart tests and v0.3.0 migration without rewriting runtime logic.
4. **Diagnostics are not UI** — `RunSummary` + narrative text give reviewers enough context without a dashboard.
5. **Experiments need controls** — comparing storage backends and denial policies produced concrete defaults, not taste calls.
6. **Adapter hooks beat runtime auth** — `ApproverValidator` keeps IdP policy in the parent platform seam without polluting core state.

## Evidence

- All **88** pytest and **7** eval baseline scenarios pass locally and in CI.
- Phase 8 experiments documented with reproducible runners in `groundseal/evaluation/experiments.py`.
- Post-review security fixes documented in [code-review-notes.md](code-review-notes.md).
- Known limitations honestly scoped in [known-limitations.md](known-limitations.md).

## Residual Risks

- Linear workflows only; DAG generalization untested.
- FileStorage locks are best-effort non-blocking; high-contention multi-writer scenarios untested.
- Cross-tenant storage isolation not enforced in core paths.

See [integration-recommendations.md](integration-recommendations.md) for backfeed guidance.

## Baseline Closure (v0.3.0)

Roadmap phases 0–9 and post-review TASKS are complete. The subsystem is suitable as a **typed integration baseline** for a parent governed-agent platform. Further work (DAG graphs, lock retry, tenant-scoped storage) is explicitly deferred in [TASKS.md](../TASKS.md).
