# TASKS.md

## Now (Post Phase 9)

- [ ] Concurrent FileStorage locking and migration strategy.
- [ ] External IdP validation for approver_id in adapter layer.
- [ ] General workflow graph loading beyond `fixture_approval_v1`.

## Completed

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
