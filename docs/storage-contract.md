# Storage Contract (Phase 6)

Persistence boundary for durable runs and checkpoints.

## StorageBackend Interface

| Method | Purpose |
|--------|---------|
| `save_run(state)` | Persist authoritative RunState |
| `load_run(run_id)` | Load run or None |
| `save_checkpoint(cp)` | Persist immutable checkpoint |
| `load_checkpoint(id)` | Load checkpoint or None |
| `list_checkpoint_ids(run_id)` | Ordered checkpoint IDs for resume |
| `has_applied_patch(run_id, patch_id)` | Duplicate patch detection |
| `mark_patch_applied(run_id, patch_id)` | Record applied patch |

## Implementations

| Backend | Module | Durability |
|---------|--------|------------|
| `MemoryStorage` | `groundseal/storage/backends.py` | Process lifetime |
| `FileStorage` | `groundseal/storage/backends.py` | JSON files on disk |

## FileStorage Layout

```text
{root}/
  runs/{run_id}.json
  checkpoints/{checkpoint_id}.json
  checkpoints/_index_{run_id}.json
  patches/{run_id}.json
```

## Lifecycle Semantics

1. **Interrupt persist**: Run and checkpoint written before returning `Interrupt` to caller.
2. **Restart resume**: New `Runtime(storage=FileStorage(same_path))` can `get_run` and `resume`.
3. **Replay drift**: Loading stale checkpoint after state advance → `STALE_CHECKPOINT` (unchanged).

## Non-Goals (Phase 6)

- Concurrent writer locking
- Migration between storage versions
- Encryption at rest

## Evaluation

See `tests/test_storage.py` for restart and patch persistence tests.
