"""Deterministic branch selection."""

from __future__ import annotations

import hashlib
import json
import uuid
from typing import Any

from groundseal.models import BranchDecision


def branch_select(context: dict[str, Any]) -> BranchDecision:
    payload = json.dumps(context, sort_keys=True)
    inputs_hash = hashlib.sha256(payload.encode()).hexdigest()
    selected_edge = "edge_a" if context.get("branch_key", "a") == "a" else "edge_b"
    return BranchDecision(
        decision_id=str(uuid.uuid5(uuid.NAMESPACE_DNS, inputs_hash)),
        inputs_hash=inputs_hash,
        selected_edge=selected_edge,
    )
