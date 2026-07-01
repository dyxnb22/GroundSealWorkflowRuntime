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

## FileStorage Layout (v2)

```text
{root}/
  _meta/
    version.json          # {"storage_version": 2}
    locks/{run_id}.lock     # per-run write locks
  runs/{run_id}.json
  checkpoints/{checkpoint_id}.json
  checkpoints/_index_{run_id}.json
  patches/{run_id}.json
```

## Migration (v1 → v2)

On `FileStorage` init, `ensure_storage_ready()`:

1. Creates root if missing.
2. Reads `_meta/version.json` (defaults to v1 when absent).
3. Migrates v1 layouts by ensuring subdirectories and `_meta/locks/` exist, then writes version 2.
4. Rejects storage versions newer than runtime support (`STORAGE_MIGRATION_FAILED`).

Migration is idempotent: re-opening an v2 root is a no-op.

## Concurrent Writes

`FileStorage` acquires a per-run file lock (`fcntl.flock` when available) before mutating run, checkpoint index, or patch files for that `run_id`. Non-blocking lock failure surfaces as `STORAGE_LOCK_TIMEOUT`.

## Lifecycle Semantics

1. **Interrupt persist**: Run and checkpoint written before returning `Interrupt` to caller.
2. **Restart resume**: New `Runtime(storage=FileStorage(same_path))` can `get_run` and `resume`.
3. **Replay drift**: Loading stale checkpoint after state advance → `STALE_CHECKPOINT` (unchanged).

## Non-Goals (Phase 6+)

- Cross-process lock timeout tuning / retry policy
- Encryption at rest
- DAG workflow graphs

## Evaluation

See `tests/test_storage.py` for restart, migration, locking, and patch persistence tests.
