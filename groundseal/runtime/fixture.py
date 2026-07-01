"""Hardcoded fixture workflow definition."""

from groundseal.models import NodeDefinition

FIXTURE_WORKFLOW_ID = "fixture_approval_v1"

FIXTURE_NODES: list[NodeDefinition] = [
    NodeDefinition(node_id="node_prepare", requires_approval=False, handler="prepare"),
    NodeDefinition(node_id="node_execute", requires_approval=True, handler="execute"),
]
