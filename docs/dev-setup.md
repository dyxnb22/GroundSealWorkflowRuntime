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
  __init__.py
  models/           # Pydantic models
  invariants/       # Pure invariant checks
  runtime/          # Phase 2 in-memory runtime
  errors.py         # Structured error types
tests/
  fixtures/         # JSON fixtures by eval category
  test_schemas.py
  test_invariants.py
  test_runtime.py
docs/
  contracts/        # Contract docs (Phase 0)
  glossary.md
  invariants.md
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

## Non-Goals (Phase 2 dev setup)

- Docker / CI pipeline (Phase 4)
- Persistent storage
- Parent platform adapter
