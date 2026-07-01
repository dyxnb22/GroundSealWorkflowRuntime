# Failure Analysis Plan

## Purpose

This document defines how GroundSealWorkflowRuntime should study failures instead of merely routing around them.

## Failure Categories

- resume inconsistency
- implicit state mutation
- branch drift between runtimes
- terminal-state ambiguity

## Required Failure Record

Each meaningful failure investigation should capture:
- the triggering input or condition
- the expected behavior
- the observed behavior
- the most likely root cause
- whether the issue is deterministic or intermittent
- what test or guard should prevent recurrence

## Review Cadence

- Review new failures before expanding scope.
- Promote repeated issues into explicit regression tests.
- Update docs when a failure changes the architecture or contract story.

## Anti-Patterns

- Closing failures with vague “needs more work” notes.
- Treating unexplained regressions as acceptable churn.
- Fixing symptoms while leaving contract ambiguity in place.
