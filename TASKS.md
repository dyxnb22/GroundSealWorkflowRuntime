# TASKS.md

## Now (Post Phase 9)

- [ ] DAG workflow graphs (beyond linear node lists).
- [ ] Cross-process lock retry policy for FileStorage.

## Completed (Post-Review Advancement v0.3.0)

- [x] Concurrent FileStorage locking (`fcntl` per-run locks)
- [x] Storage migration v1→v2 (`ensure_storage_ready`, `_meta/version.json`)
- [x] External IdP validation hook (`ApproverValidator` in adapter)
- [x] Workflow registry + JSON graph loading (`workflows/*.json`)
- [x] Tests (88), docs: [workflow-definition.md](docs/contracts/workflow-definition.md)

## Completed (Code Review Polish)

- [x] Close approval bypass via reserved context keys
- [x] Runtime module split, `persist_run`, module-level `run`/`resume`
- [x] FileStorage atomic writes, ID validation, corrupt load errors
- [x] Expanded tests (70), per-scenario eval ratchet
- [x] [code-review-notes.md](docs/code-review-notes.md)

### Phase 9
- [x] [case-study.md](docs/case-study.md)
- [x] [integration-recommendations.md](docs/integration-recommendations.md)

### Phase 8
- [x] Storage backend comparison experiment
- [x] Approval denial policy comparison (`ApprovalDenialPolicy`)
- [x] [experiments/decision-memo.md](docs/experiments/decision-memo.md)
- [x] `tests/test_experiments.py`

### Phase 7
- [x] Diagnostic report schema (`groundseal/diagnostics/`)
- [x] Human-readable run summary and narrative
- [x] [review-ux-notes.md](docs/review-ux-notes.md)
- [x] Adapter diagnostic integration
- [x] `tests/test_diagnostics.py`

### Phase 6–0
- [x] See prior TASKS entries (storage, adapter, eval baseline, runtime core, contracts)

## Sequencing Rules

- Prefer docs -> contracts -> tests -> implementation.
- Avoid broad implementation until phase exit criteria are explicit.
- Keep tasks small enough for one focused agent round to complete well.
