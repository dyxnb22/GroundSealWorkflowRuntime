# GroundSealWorkflowRuntime

A typed, interruptible, resumable workflow runtime for governed agents

## Overview

GroundSealWorkflowRuntime is a long-horizon learning and engineering project focused on state models, node contracts, checkpoints, approval interruption, resume semantics, deterministic branching, and workflow diagnostics.
It is intentionally scoped as a standalone subsystem so it can later plug back
into a governed enterprise-agent platform without inheriting that platform's
full codebase or accidental complexity on day one.

## Why This Exists

Many agent runtimes blur planning, execution, and side effects. This project isolates the runtime so long-lived workflows can be paused, resumed, audited, and reasoned about independently.

## What This Project Is

- A subsystem-first engineering project with explicit contracts.
- A documentation-led project intended for sustained Cursor Cloud Agent work.
- A place to learn one difficult slice of enterprise agent systems deeply.
- A project that should produce reusable contracts, tests, and design notes.

## What This Project Is Not

- building every workflow app at once
- tying the runtime to a single model provider
- hiding state transitions inside prompt logic
- not a generic chatbot wrapper
- not a fast demo optimized for screenshots instead of understanding

## Core Capability Scope

- run state schema
- node patch model
- checkpoint contract
- interrupt and resume rules
- workflow invariants

## Planned Interfaces

- `run(initial_state) -> final_state`
- `resume(run_id) -> state`
- `apply_patch(state, patch) -> state`
- `emit_checkpoint(state)`

## Documentation Map

- `PROJECT_BRIEF.md` — project framing, goals, non-goals, and learning value.
- `AGENTS.md` — default execution rules for future agents.
- `TASKS.md` — prioritized task breakdown for now, next, and later.
- `docs/architecture.md` — subsystem map and trust boundaries.
- `docs/design-principles.md` — design rules and tradeoff posture.
- `docs/coding-guidelines.md` — implementation discipline once code starts.
- `docs/roadmap.md` — phased long-term execution plan.
- `docs/evaluation-plan.md` — how quality and regressions will be measured.
- `docs/failure-analysis-plan.md` — how failures are classified and reviewed.
- `docs/execution-rhythm.md` — how to keep long-running agent work disciplined.
- `docs/integration-contract.md` — how this project will plug back into larger systems.
- `docs/open-questions.md` — unresolved research and implementation questions.

## Current Stage

Stage 0 is complete only when the project has clear contracts, explicit
non-goals, phase boundaries, evaluation intent, and Cursor rules strong enough
to keep parallel implementation work on track.

## Relationship To The Parent Platform

This project is intentionally narrower than the original platform. It should
become better than the parent implementation at its own specialty, then feed
stable contracts and lessons back into the broader system.
