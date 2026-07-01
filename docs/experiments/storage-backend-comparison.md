# Experiment: Storage Backend Comparison (Phase 8)

## Hypothesis

FileStorage enables cross-session resume after interrupt; MemoryStorage does not survive process restart.

## Setup

- Workflow: `fixture_approval_v1` with approval interrupt at `node_execute`.
- Backends: `MemoryStorage` vs `FileStorage` (temp directory).
- Control: same clock, same initial context, deterministic run IDs per backend.

## Observations

Run `groundseal.evaluation.experiments.run_storage_backend_experiment()` or `pytest tests/test_experiments.py`.

| Backend | Completes after interrupt | Survives restart | Artifacts |
|---------|---------------------------|------------------|-----------|
| memory | yes (same process) | N/A in-process | 0 files |
| file | yes (new Runtime instance) | yes | JSON files under storage root |

## Tradeoffs

| | MemoryStorage | FileStorage |
|---|---------------|-------------|
| Simplicity | higher | lower |
| Durability | none | survives restart |
| Test speed | faster | slightly slower |
| Ops visibility | none | inspectable JSON files |

## Conclusion

**Chosen default**: MemoryStorage for unit tests and deterministic CI.

**When to use FileStorage**: production-like runs requiring interrupt/resume across process boundaries.

See [decision-memo.md](decision-memo.md).
