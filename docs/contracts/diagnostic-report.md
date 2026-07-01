# Diagnostic Report Contract (Phase 7)

## Purpose

Provide operator/reviewer-readable artifacts without exposing raw internal structures.

## DiagnosticReport Schema

| Field | Type | Description |
|-------|------|-------------|
| `run_id` | string | Target run |
| `summary` | RunSummary | Human-reviewable summary |
| `invariant_status` | `ok` \| `violation` | Current invariant check |
| `review_hints` | list[string] | Suggested reviewer actions |
| `raw_status` | string | RunStatus value |

## RunSummary Schema

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Run status |
| `state_version` | integer | Current version |
| `workflow_phase` | string | e.g. `awaiting_approval_at:node_execute` |
| `nodes` | list[NodeSummary] | Completed node outputs (keys only) |
| `checkpoints` | list[CheckpointSummary] | Checkpoint timeline |
| `branches` | list[BranchSummary] | Branch decisions (truncated hash) |
| `context_keys` | list[string] | Context field names (not values) |
| `narrative` | string | One-paragraph plain-language summary |

## API

```python
from groundseal.diagnostics import build_diagnostic_report, format_run_summary_text

report = build_diagnostic_report(runtime, run_id)
text = format_run_summary_text(report.summary)
```

## Adapter Integration

`PlatformAdapter.start_run(..., include_diagnostic=True)` attaches `DiagnosticReport` to response.

`PlatformAdapter.get_diagnostic_report(run_id)` fetches report for existing runs.

## Redaction

- Context values are not included in summary by default; only keys.
- Full state remains in RunState for authorized programmatic access.

Implementation: `groundseal/diagnostics/report.py`
