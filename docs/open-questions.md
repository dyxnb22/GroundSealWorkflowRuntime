# Open Questions

## Resolved (Phase 0)

- **Authoritative contract surface**: [contracts/public-api.md](contracts/public-api.md) — `run`, `resume`, `apply_patch`, `emit_checkpoint`.
- **Untrusted inputs**: all caller-supplied fields; normalized via Pydantic validation and invariant checks before mutation.
- **Evidence preserved**: checkpoints (full state snapshot), branch decisions, node results, structured error envelopes.
- **Acceptable fallback**: none for high-risk ambiguity; fail closed per [design-principles.md](design-principles.md).
- **Deterministic from day one**: branch decisions, fixture workflow execution, checkpoint/resume path, schema validation.
- **Smallest teaching slice**: linear 2-node fixture with approval interrupt and resume ([dev-setup.md](dev-setup.md)).
- **Failure fixtures**: five evaluation case categories in [evaluation-plan.md](evaluation-plan.md).

## Still Open

- Which tradeoffs are likely to be architecture-defining rather than local?
- Where should integration boundaries stop to avoid subsystem creep beyond Phase 5?

## Questions Best Deferred Until After A Baseline Exists

- performance optimization tradeoffs
- richer UX or service wrappers
- storage or framework expansion beyond the minimum viable shape
- multi-tenant isolation in core state vs adapter-only
