"""Shared constants for trust boundaries."""

# Runtime-internal context keys — callers must not set these in RunInitialState.
INTERNAL_CONTEXT_KEYS = frozenset({"_approval_granted", "approver_id", "_workflow_id"})

# Reserved context key prefix for runtime-managed fields.
INTERNAL_CONTEXT_PREFIX = "_"
