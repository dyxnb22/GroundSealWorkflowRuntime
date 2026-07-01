# Glossary

Canonical vocabulary for GroundSealWorkflowRuntime. Use these terms consistently across contracts, code, and evaluation fixtures.

## Run

A **Run** is a single workflow execution instance bounded by a unique `run_id`. A Run begins when `run(initial_state)` is accepted and ends when the runtime reaches a **TerminalState** or an OPTIONS are exhausted by policy.

- Ownership: the runtime owns Run lifecycle; callers supply initial input but cannot silently override invariants.
- Scope: one Run maps to one linear or branched execution trace within this subsystem.

## State

**State** (`RunState`) is the authoritative runtime snapshot for a Run. It holds workflow progress, node outcomes, branch decisions, and metadata required for resume.

- Ownership: the runtime is the sole mutator; changes occur only via validated **Patch** application or controlled node execution.
- Versioning: each mutation increments `state_version` (monotonic integer starting at 0).

## Node

A **Node** is an atomic execution unit with a typed input/output contract. Nodes transition through a defined lifecycle (see [node-contract.md](contracts/node-contract.md)).

- Ownership: node definitions are workflow-local; the runtime enforces lifecycle transitions.

## Patch

A **Patch** is an atomic, typed description of a change to RunState. Patches are the only permitted explicit state mutation mechanism outside node execution.

- Ownership: callers may propose patches; the runtime validates and applies or rejects them (fail closed).

## Checkpoint

A **Checkpoint** is an immutable snapshot of RunState plus metadata sufficient to resume execution. Produced by `emit_checkpoint(state)`.

- Ownership: the runtime writes checkpoints; callers read checkpoint IDs for resume requests.

## Interrupt

An **Interrupt** pauses a Run before side effects proceed, typically for human **approval**. The Run enters `interrupted` status with a recorded reason and checkpoint reference.

- Triggers: policy-driven (e.g., node requires approval), not implicit prompt behavior.

## Resume

**Resume** continues a previously interrupted Run from the latest valid checkpoint after supplied approval (or other resume token) is validated.

- Rule: resume must not skip invariant checks or apply stale state without explicit handling.

## Branch

A **Branch** is a deterministic routing decision selecting the next node based on typed inputs derived from RunState. Same inputs must yield the same branch outcome (no randomness in Phase 2 slice).

## TerminalState

A **TerminalState** is a Run status from which no further node execution or patch application is permitted: `completed`, `failed`, or `cancelled`.

- Rule: once terminal, `apply_patch` and `resume` reject unless explicitly documented otherwise (none in Phase 2).

## Platform-Neutral vs Adapter-Local

| Category | Examples | Boundary |
|----------|----------|----------|
| Platform-neutral | `run_id`, `RunState`, `Patch`, `Checkpoint`, error codes | Defined in subsystem contracts; stable across integrations |
| Adapter-local | tenancy ID, user identity, external audit sink IDs | Owned by parent platform adapter; not embedded in core state |

## Related Documents

- [architecture.md](architecture.md) — component map and trust boundaries
- [contracts/](contracts/) — typed contract definitions
- [invariants.md](invariants.md) — rules that must always hold (Phase 1+)
