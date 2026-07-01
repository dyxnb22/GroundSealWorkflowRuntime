"""Workflow definition models and registry."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from groundseal.errors import GroundSealError
from groundseal.models import NodeDefinition
from groundseal.runtime.fixture import FIXTURE_NODES, FIXTURE_WORKFLOW_ID


class WorkflowDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workflow_id: str
    version: str = "1"
    description: str = ""
    nodes: list[NodeDefinition] = Field(min_length=1)


class WorkflowRegistry:
    """In-memory registry of loadable workflow graphs (linear node order)."""

    def __init__(self) -> None:
        self._workflows: dict[str, WorkflowDefinition] = {}

    def register(self, workflow: WorkflowDefinition) -> None:
        if not workflow.nodes:
            raise GroundSealError(
                code="INVALID_WORKFLOW",
                message="Workflow must define at least one node",
                details={"workflow_id": workflow.workflow_id},
            )
        self._workflows[workflow.workflow_id] = workflow

    def get(self, workflow_id: str) -> WorkflowDefinition:
        wf = self._workflows.get(workflow_id)
        if wf is None:
            raise GroundSealError(
                code="WORKFLOW_NOT_FOUND",
                message="Unknown workflow_id",
                details={"workflow_id": workflow_id},
            )
        return wf

    def load_json_file(self, path: Path | str) -> WorkflowDefinition:
        data = json.loads(Path(path).read_text())
        workflow = WorkflowDefinition.model_validate(data)
        self.register(workflow)
        return workflow

    def load_directory(self, directory: Path | str) -> int:
        count = 0
        for file in sorted(Path(directory).glob("*.json")):
            self.load_json_file(file)
            count += 1
        return count


def default_registry() -> WorkflowRegistry:
    """Registry with built-in fixture_approval_v1."""
    registry = WorkflowRegistry()
    registry.register(
        WorkflowDefinition(
            workflow_id=FIXTURE_WORKFLOW_ID,
            version="1",
            description="Linear prepare → execute with approval gate",
            nodes=list(FIXTURE_NODES),
        )
    )
    return registry
