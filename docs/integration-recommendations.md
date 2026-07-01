# Integration Recommendations (Phase 9)

How a parent governed-agent platform should consume GroundSealWorkflowRuntime.

## Recommended Integration Pattern

```text
Parent Orchestrator
  → PlatformAdapter.start_run(PlatformRunRequest)
  ← PlatformRunResponse (interrupt | run_state | error)
  → Human approval UI (if interrupt)
  → PlatformAdapter.resume_run(...)
  → PlatformAdapter.get_diagnostic_report(run_id)  # for audit ticket
```

## Do

- Keep `tenant_id` / `caller_id` in adapter envelope only.
- Use `include_diagnostic=True` on interrupt responses for operator tooling.
- Persist runs via `FileStorage` when workflows span process restarts.
- Run `scripts/run_eval.py` in CI before promoting runtime changes.
- Map subsystem error codes to platform-level alerts ([failure-taxonomy.md](failure-taxonomy.md)).

## Do Not

- Embed prompts or LLM calls inside runtime node handlers.
- Bypass `apply_patch` to mutate RunState directly.
- Suppress `APPROVAL_DENIED` or `STALE_CHECKPOINT` errors.
- Store tenant identifiers in `RunState.context`.

## Suggested Platform Seams

| Platform concern | GroundSeal seam |
|------------------|-----------------|
| AuthZ | Wrap `PlatformAdapter.resume_run` with platform policy |
| Audit log | Subscribe to `PlatformRunResponse.evidence` + diagnostic JSON |
| Durability | Inject `FileStorage(root=platform_data_dir)` |
| Observability | Export `DiagnosticReport.summary.narrative` to tickets |

## Migration Path

1. Replace ad-hoc pause/resume logic with adapter calls.
2. Add diagnostic reports to existing approval UI.
3. Enable FileStorage for runs exceeding single-process lifetime.
4. Ratchet eval baseline when intentionally changing behavior.

## Backfeed to Platform Understanding

This subsystem demonstrates that **workflow state should be a typed, testable contract** — not implicit conversation history. Parent platforms benefit by:

- Narrowing runtime responsibilities
- Making approval gates explicit and resumable
- Measuring regressions with fixtures instead of manual QA

## Open Integration Work

- External IdP integration for `approver_id` validation
- Multi-workflow graph loading (beyond `fixture_approval_v1`)
- Cross-tenant storage isolation in FileStorage paths
