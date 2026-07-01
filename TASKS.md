# TASKS.md

## Now (Phase 3)

- [ ] Expand negative-path tests beyond Phase 2 baseline (adversarial inputs, malformed resume).
- [ ] Promote failure taxonomy entries into dedicated regression fixtures.
- [ ] Document repair notes for any newly discovered failure clusters.

## Next (Phase 4–5)

- [ ] Add evaluation baseline ratchet and CI reporting.
- [ ] Define parent platform adapter handshake tests.
- [ ] Extend [integration-contract.md](docs/integration-contract.md) with adapter examples.

## Later (Phase 6+)

- Persistent checkpoint storage and replay semantics.
- Operator diagnostics and review UX.
- Comparative architectural experiments and case study.

## Completed

### Phase 2
- [x] In-memory runtime: `run`, `resume`, `apply_patch`, `emit_checkpoint`
- [x] `fixture_approval_v1` two-node workflow with approval interrupt
- [x] Deterministic tests for five evaluation case categories (30 tests)
- [x] [known-limitations.md](docs/known-limitations.md)

### Phase 1
- [x] Pydantic models from [docs/contracts/](docs/contracts/)
- [x] Schema and invariant tests with JSON fixtures
- [x] [docs/invariants.md](docs/invariants.md)

### Phase 0
- [x] Glossary and boundary language — [docs/glossary.md](docs/glossary.md)
- [x] Minimal contract set — [docs/contracts/](docs/contracts/)
- [x] Evaluation case categories — [docs/evaluation-plan.md](docs/evaluation-plan.md)
- [x] Platform-neutral vs adapter-local boundaries — [docs/integration-contract.md](docs/integration-contract.md)
- [x] Local dev shape — [docs/dev-setup.md](docs/dev-setup.md)

## Sequencing Rules

- Prefer docs -> contracts -> tests -> implementation.
- Avoid broad implementation until phase exit criteria are explicit.
- Keep tasks small enough for one focused agent round to complete well.
