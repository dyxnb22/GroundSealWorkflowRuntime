# Integration Contract

## Role In A Larger System

GroundSealWorkflowRuntime plugs into a parent platform as a specialized subsystem rather than a hidden helper module. See [glossary.md](glossary.md) for platform-neutral vs adapter-local boundaries.

## Integration Expectations

- Callers provide typed input (`RunInitialState`, `ResumeInput`, `Patch`), not arbitrary prompts.
- Callers receive typed output (`RunState`, `Interrupt`, `Checkpoint`) plus structured errors.
- Subsystem invariants remain enforced even when the parent platform wants convenience.
- Failure states are explicit and machine-readable (see [contracts/public-api.md](contracts/public-api.md)).

## Desired Boundary Shape

- thin adapter layer
- explicit request and response schemas
- deterministic local mode for testing
- minimal assumptions about the rest of the platform

## Platform-Neutral Types (stable)

| Type | Contract doc |
|------|----------------|
| `RunState` | [run-state.md](contracts/run-state.md) |
| `Patch` | [patch-model.md](contracts/patch-model.md) |
| `Checkpoint` | [checkpoint.md](contracts/checkpoint.md) |
| `Interrupt` / `ResumeInput` | [interrupt-resume.md](contracts/interrupt-resume.md) |
| Public API | [public-api.md](contracts/public-api.md) |

## Adapter-Local Concerns (parent platform)

- tenancy and identity enforcement
- external audit sink routing
- authZ for approval actions
- persistence backend selection (Phase 6+)

## Questions To Resolve Later

- where tenancy and identity should be enforced in the adapter
- what belongs in shared contracts versus subsystem-local models as the parent evolves
- how much evidence should flow back to the caller by default
