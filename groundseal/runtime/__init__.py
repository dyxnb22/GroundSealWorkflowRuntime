"""Public runtime API."""

from __future__ import annotations

from groundseal.models import (
    ApprovalDenialPolicy,
    Checkpoint,
    CheckpointReason,
    Interrupt,
    Patch,
    ResumeInput,
    RunInitialState,
    RunState,
)
from groundseal.runtime.branching import branch_select
from groundseal.runtime.checkpointing import emit_checkpoint
from groundseal.runtime.engine import InMemoryRuntime, Runtime
from groundseal.runtime.fixture import FIXTURE_NODES, FIXTURE_WORKFLOW_ID
from groundseal.runtime.patching import ALLOWED_PATCH_PREFIX, apply_patch
from groundseal.storage import MemoryStorage, StorageBackend

__all__ = [
    "ALLOWED_PATCH_PREFIX",
    "FIXTURE_NODES",
    "FIXTURE_WORKFLOW_ID",
    "InMemoryRuntime",
    "Runtime",
    "apply_patch",
    "branch_select",
    "emit_checkpoint",
    "run",
    "resume",
]


def run(
    initial: RunInitialState,
    *,
    storage: StorageBackend | None = None,
    clock: str | None = None,
    denial_policy: ApprovalDenialPolicy = ApprovalDenialPolicy.FAIL_RUN,
) -> RunState | Interrupt:
    """Module-level convenience wrapper matching contract docs."""
    return Runtime(storage=storage, clock=clock, denial_policy=denial_policy).run(initial)


def resume(
    resume_input: ResumeInput,
    *,
    storage: StorageBackend | None = None,
    clock: str | None = None,
    denial_policy: ApprovalDenialPolicy = ApprovalDenialPolicy.FAIL_RUN,
) -> RunState | Interrupt:
    """Module-level convenience wrapper matching contract docs."""
    return Runtime(storage=storage, clock=clock, denial_policy=denial_policy).resume(resume_input)
