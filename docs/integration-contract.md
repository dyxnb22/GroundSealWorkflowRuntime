# Integration Contract

## Role In A Larger System

GroundSealWorkflowRuntime should plug into a parent platform as a specialized subsystem rather than a hidden helper module.

## Integration Expectations

- Callers provide typed input, not arbitrary prompts.
- Callers receive typed output plus enough evidence to understand the result.
- Subsystem invariants remain enforced even when the parent platform wants convenience.
- Failure states are explicit and machine-readable.

## Desired Boundary Shape

- thin adapter layer
- explicit request and response schemas
- deterministic local mode for testing
- minimal assumptions about the rest of the platform

## Questions To Resolve Later

- which types must stay platform-neutral
- where tenancy and identity should be enforced
- what belongs in shared contracts versus subsystem-local models
- how much evidence should flow back to the caller by default
