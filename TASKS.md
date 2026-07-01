# TASKS.md

## Now (Phase 7)

- [ ] Define diagnostic report schema for operator/reviewer consumption.
- [ ] Add human-readable run summary from RunState + checkpoints.
- [ ] Document review UX notes without building full UI.

## Next (Phase 8–9)

- [ ] Compare at least two architectural approaches (e.g., storage backends, approval policies).
- [ ] Produce case-study summary and integration backfeed memo.

## Later

- Concurrent storage locking and migration strategy.
- Richer parent platform authZ integration in adapter.

## Completed

### Phase 6
- [x] StorageBackend abstraction and FileStorage JSON persistence
- [x] Multi-session interrupt/resume tests (`tests/test_storage.py`)
- [x] [storage-contract.md](docs/storage-contract.md)

### Phase 5
- [x] PlatformAdapter and adapter contract
- [x] Integration boundary tests
- [x] Extended [integration-contract.md](docs/integration-contract.md)

### Phase 4
- [x] Evaluation baseline runner and ratchet (`groundseal/evaluation/`, `scripts/run_eval.py`)
- [x] Committed [eval/baseline.json](eval/baseline.json)
- [x] GitHub Actions CI workflow
- [x] [evaluation-baseline-report.md](docs/evaluation-baseline-report.md)

### Phase 3
- [x] Input validation layer (`groundseal/validation/`)
- [x] Negative-path regression tests (`tests/test_failure_paths.py`)
- [x] [failure-taxonomy.md](docs/failure-taxonomy.md) and [repair-notes.md](docs/repair-notes.md)

### Phase 2
- [x] In-memory runtime and 30+ core tests
- [x] [known-limitations.md](docs/known-limitations.md)

### Phase 1 & 0
- [x] Schemas, invariants, contracts, glossary — see prior entries

## Sequencing Rules

- Prefer docs -> contracts -> tests -> implementation.
- Avoid broad implementation until phase exit criteria are explicit.
- Keep tasks small enough for one focused agent round to complete well.
