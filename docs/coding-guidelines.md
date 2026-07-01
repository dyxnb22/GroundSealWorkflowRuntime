# Coding Guidelines

## Purpose

These guidelines apply once implementation begins in GroundSealWorkflowRuntime.

## Implementation Rules

- Keep code aligned to the current roadmap phase.
- Build around typed models and explicit interfaces.
- Make validation boundaries obvious.
- Prefer small modules with single responsibilities.
- Write comments only where reasoning or invariants are non-obvious.

## Test Rules

- Add tests proportional to risk and blast radius.
- Prefer deterministic fixtures over live dependencies.
- Cover both positive and negative paths.
- Preserve regression tests once a bug has been found.

## Dependency Rules

- Keep dependencies minimal.
- Prefer the standard library or existing project utilities when suitable.
- Introduce new frameworks only with a documented reason.

## Review Checklist

- Is the phase alignment clear?
- Is the contract surface still small and explicit?
- Are invariants enforced in code, not only described in docs?
- Is there enough evidence to justify the change?
