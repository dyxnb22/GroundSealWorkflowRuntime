# Development Setup

## Technology Stack (Phase 1–2)

- **Language**: Python 3.11+
- **Schemas**: Pydantic v2
- **Tests**: pytest
- **Dependencies**: minimal (`pydantic` only for runtime; `pytest` for dev)

Rationale: contract-first validation, deterministic fixtures, low dependency surface.

## Directory Layout

```text
groundseal/
  models/           # Pydantic models
  invariants/       # Invariant checks
  runtime/          # Runtime engine
  adapter/          # Phase 5 platform adapter
  evaluation/       # Phase 4 baseline runner
  storage/          # Phase 6 persistence backends
  validation/       # Phase 3 input validation
  errors.py
tests/
  fixtures/         # JSON fixtures by eval category
  test_*.py
eval/
  baseline.json     # Ratcheted evaluation baseline
scripts/
  run_eval.py
docs/
  contracts/
pyproject.toml
```

## Local Commands

```bash
# Create virtualenv and install
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest -v

# Run evaluation baseline
python scripts/run_eval.py --report

# Export JSON schemas (optional)
python -c "from groundseal.models import export_schemas; export_schemas()"
```

## Fixture Workflow (Phase 2)

Hardcoded linear workflow `fixture_approval_v1`:

1. `node_prepare` — no approval; sets context fields
2. `node_execute` — requires approval; interrupt before completion

No external services, models, or databases in Phase 2.

## Determinism Rules

- Timestamps injected via `clock` parameter in tests (fixed ISO8601 strings).
- `run_id` and UUIDs supplied by fixtures where reproducibility matters.
- No network, randomness, or wall-clock dependence in tests.

## Non-Goals

- Concurrent multi-writer storage
- Full operator UI (Phase 7)
- External model or LLM integration
