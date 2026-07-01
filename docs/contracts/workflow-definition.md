# Workflow Definition Contract (Post Phase 9)

Linear workflow graphs loadable from JSON and registered at runtime startup.

## WorkflowDefinition

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `workflow_id` | string | yes | Stable identifier referenced by `RunInitialState.workflow_id` |
| `version` | string | no | Definition version label (default `"1"`) |
| `description` | string | no | Human-readable summary |
| `nodes` | list[NodeDefinition] | yes | Ordered linear execution (min length 1) |

Each `NodeDefinition` follows [node-contract.md](node-contract.md): `node_id`, `requires_approval`, `handler`.

## WorkflowRegistry

| Method | Purpose |
|--------|---------|
| `register(workflow)` | Add or replace a definition in memory |
| `get(workflow_id)` | Resolve definition or raise `WORKFLOW_NOT_FOUND` |
| `load_json_file(path)` | Parse JSON, validate, register |
| `load_directory(dir)` | Load all `*.json` files in directory |

`default_registry()` ships with built-in `fixture_approval_v1` for backward compatibility.

## JSON Example

```json
{
  "workflow_id": "linear_no_approval_v1",
  "version": "1",
  "description": "Single-node workflow without approval",
  "nodes": [
    {"node_id": "node_prepare", "requires_approval": false, "handler": "prepare"}
  ]
}
```

Sample files live in `workflows/`.

## Runtime Integration

1. Caller passes `workflow_id` in `RunInitialState`.
2. Runtime resolves nodes from registry and stores `_workflow_id` in run context (internal, not caller-settable).
3. Resume uses stored `_workflow_id` to locate node definitions.

## Limits

- Linear node order only (no DAG branching in this slice).
- Handlers are fixture handlers (`prepare`, `execute`) until node executor expansion.

Implementation: `groundseal/workflow/registry.py`
