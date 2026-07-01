# Node Contract

## Purpose

Define execution unit lifecycle and typed I/O boundaries for workflow nodes.

## Node Lifecycle

```text
pending → running → completed
                 ↘ failed
                 ↘ interrupted (approval or policy halt)
```

| Status | Meaning |
|--------|---------|
| `pending` | Scheduled but not yet started |
| `running` | Execution in progress |
| `completed` | Finished successfully; output recorded in RunState |
| `failed` | Terminal failure; error recorded |
| `interrupted` | Paused awaiting external input (e.g., approval) |

## Node Definition (fixture workflow)

| Field | Type | Required |
|-------|------|----------|
| `node_id` | string | yes |
| `requires_approval` | boolean | yes |
| `handler` | string | yes | Logical handler name (deterministic stub in Phase 2) |

## Execution Rules

1. A node may start only when all predecessor nodes in the fixture graph are `completed`.
2. If `requires_approval` is true, the runtime transitions to `interrupted` before invoking side effects, emits a checkpoint, and returns control to the caller.
3. On success, output is merged into `node_results` and status becomes `completed`.
4. On unrecoverable error, status becomes `failed` and Run status becomes `failed` (terminal).

## Input / Output Contract

- **Input**: derived from RunState `context` and predecessor `node_results` (read-only).
- **Output**: JSON-serializable object stored under `node_results[node_id].output`.

## Fail Closed

- Invalid node_id in transition requests → reject with `NODE_NOT_FOUND`.
- Starting a node when Run is terminal → reject with `RUN_TERMINAL`.
- Double-start of the same node → reject with `NODE_ALREADY_STARTED`.
