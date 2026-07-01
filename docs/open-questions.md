# Open Questions

- Which parts of GroundSealWorkflowRuntime must be deterministic from day one, and which can be deferred?
- What is the smallest implementation slice that will still teach something real?
- Which failure modes deserve dedicated fixtures instead of informal notes?
- Where should integration boundaries stop to avoid subsystem creep?
- Which tradeoffs are likely to be architecture-defining rather than local?

## Questions That Should Be Answered Before Broad Implementation

- what is the authoritative contract surface
- what inputs are untrusted and how they are normalized
- what evidence must always be preserved
- what counts as an acceptable fallback path

## Questions Best Deferred Until After A Baseline Exists

- performance optimization tradeoffs
- richer UX or service wrappers
- storage or framework expansion beyond the minimum viable shape
