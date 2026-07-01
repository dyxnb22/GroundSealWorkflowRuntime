"""Workflow registry and JSON graph loading tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from groundseal.errors import GroundSealError
from groundseal.models import RunInitialState, RunStatus
from groundseal.runtime import Runtime
from groundseal.storage import MemoryStorage
from groundseal.workflow import WorkflowDefinition, WorkflowRegistry, default_registry
from tests.conftest import CLOCK, run_to_completion

WORKFLOWS_DIR = Path(__file__).parent.parent / "workflows"


class TestWorkflowRegistry:
    def test_default_registry_has_fixture(self) -> None:
        registry = default_registry()
        wf = registry.get("fixture_approval_v1")
        assert wf.workflow_id == "fixture_approval_v1"
        assert len(wf.nodes) == 2

    def test_load_json_file(self) -> None:
        registry = WorkflowRegistry()
        wf = registry.load_json_file(WORKFLOWS_DIR / "linear_no_approval_v1.json")
        assert wf.workflow_id == "linear_no_approval_v1"
        assert len(wf.nodes) == 1
        assert wf.nodes[0].requires_approval is False

    def test_load_directory(self) -> None:
        registry = WorkflowRegistry()
        count = registry.load_directory(WORKFLOWS_DIR)
        assert count >= 2
        assert registry.get("linear_no_approval_v1").workflow_id == "linear_no_approval_v1"

    def test_unknown_workflow_raises(self) -> None:
        registry = WorkflowRegistry()
        with pytest.raises(GroundSealError) as exc:
            registry.get("missing-workflow")
        assert exc.value.code == "WORKFLOW_NOT_FOUND"

    def test_empty_nodes_rejected_at_json_load(self) -> None:
        registry = WorkflowRegistry()
        bad_path = Path(__file__).parent / "_tmp_empty_workflow.json"
        bad_path.write_text('{"workflow_id": "empty", "nodes": []}')
        try:
            with pytest.raises(Exception):
                registry.load_json_file(bad_path)
        finally:
            bad_path.unlink(missing_ok=True)


class TestWorkflowRuntime:
    def test_linear_no_approval_completes_without_interrupt(self) -> None:
        registry = WorkflowRegistry()
        registry.load_json_file(WORKFLOWS_DIR / "linear_no_approval_v1.json")
        rt = Runtime(storage=MemoryStorage(), clock=CLOCK, workflow_registry=registry)
        state = rt.run(
            RunInitialState(
                workflow_id="linear_no_approval_v1",
                run_id="wf-linear-001",
                context={"branch_key": "a"},
            )
        )
        assert state.status == RunStatus.COMPLETED
        assert "_workflow_id" in state.context
        assert state.context["_workflow_id"] == "linear_no_approval_v1"

    def test_json_fixture_approval_matches_default(self) -> None:
        registry = WorkflowRegistry()
        registry.load_json_file(WORKFLOWS_DIR / "fixture_approval_v1.json")
        rt = Runtime(storage=MemoryStorage(), clock=CLOCK, workflow_registry=registry)
        initial = RunInitialState(
            workflow_id="fixture_approval_v1",
            run_id="wf-fixture-json-001",
            context={},
        )
        state = run_to_completion(rt, initial)
        assert state.status == RunStatus.COMPLETED
        assert "node_execute" in state.node_results
