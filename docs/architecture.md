# Architecture

## Purpose

This document defines the subsystem shape for GroundSealWorkflowRuntime, including trust
boundaries, main components, and integration seams.

## Core Responsibilities

GroundSealWorkflowRuntime owns **Run** lifecycle, authoritative **RunState**, **Node** execution contracts, **Patch** validation, **Checkpoint** emission, **Interrupt/Resume** semantics, deterministic **Branch** decisions, and workflow diagnostics evidence.

See [glossary.md](glossary.md) for canonical terms.

## Conceptual Components

1. Contract layer
   Defines the public types, state transitions, and validation rules.
2. Policy and invariants layer
   Encodes what must always hold true even when the implementation evolves.
3. Execution layer
   Performs the subsystem's work while staying inside policy and contract boundaries.
4. Evidence layer
   Captures decisions, outputs, and verification artifacts where relevant.
5. Integration adapter layer
   Keeps parent-system coupling thin and explicit.

## Trust Boundaries

- External inputs are untrusted.
- Local configuration is constrained by subsystem invariants.
- Integration callers may request behavior but must not silently override contracts.
- Debug visibility must not weaken safety or redaction requirements.

## Architectural Preferences

- Typed schemas over ad-hoc dictionaries.
- Deterministic behavior over cleverness.
- Narrow public interfaces over deep cross-module imports.
- Explicit failure modes over silent fallback.

## Initial Build Strategy

Start with the thinnest slice that proves the subsystem contract, then add
richer storage, adapters, or UI only after baseline correctness and evaluation
scaffolding exist.

## Contract References

Typed contracts live in [contracts/](contracts/). The public API surface is defined in [contracts/public-api.md](contracts/public-api.md).
