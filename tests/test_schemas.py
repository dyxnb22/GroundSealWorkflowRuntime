"""Schema validation tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from groundseal.models import Patch, RunInitialState, RunState

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


class TestRunInitialState:
    def test_valid_happy_path(self) -> None:
        data = _load("happy_path_run_complete/valid.json")
        model = RunInitialState.model_validate(data)
        assert model.workflow_id == "fixture_approval_v1"

    def test_invalid_unknown_workflow(self) -> None:
        data = _load("happy_path_run_complete/invalid.json")
        with pytest.raises(ValidationError):
            RunInitialState.model_validate({**data, "workflow_id": 123})

    def test_valid_interrupt_fixture(self) -> None:
        data = _load("interrupt_at_approval_then_resume/valid.json")
        model = RunInitialState.model_validate(data)
        assert model.run_id is not None


class TestRunState:
    def test_valid_terminal(self) -> None:
        data = _load("run_state/valid_terminal.json")
        state = RunState.model_validate(data)
        assert state.status.value == "completed"
        assert state.current_node_id is None

    def test_valid_running(self) -> None:
        data = _load("run_state/valid_running.json")
        state = RunState.model_validate(data)
        assert state.current_node_id == "node_prepare"

    def test_invalid_negative_version(self) -> None:
        data = _load("run_state/invalid_bad_version.json")
        data["state_version"] = -1
        with pytest.raises(ValidationError):
            RunState.model_validate(data)

    def test_invalid_extra_fields_forbidden(self) -> None:
        data = _load("run_state/valid_running.json")
        data["unknown_field"] = True
        with pytest.raises(ValidationError):
            RunState.model_validate(data)


class TestPatch:
    def test_valid_patch_fixture(self) -> None:
        data = _load("invalid_patch_rejected/valid.json")
        patch = Patch.model_validate(data["patch"])
        assert patch.target_version == 1

    def test_invalid_patch_missing_ops(self) -> None:
        with pytest.raises(ValidationError):
            Patch.model_validate({"patch_id": "x", "target_version": 0, "operations": "bad"})

    def test_invalid_patch_negative_version(self) -> None:
        data = _load("invalid_patch_rejected/valid.json")
        bad = {**data["patch"], "target_version": -1}
        with pytest.raises(ValidationError):
            Patch.model_validate(bad)
