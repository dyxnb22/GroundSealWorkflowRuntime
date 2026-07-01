"""Phase 8 comparative experiment tests."""

from __future__ import annotations

from pathlib import Path

from groundseal.evaluation.experiments import (
    run_approval_policy_experiment,
    run_storage_backend_experiment,
)


class TestStorageBackendExperiment:
    def test_file_storage_survives_restart(self, tmp_path: Path) -> None:
        report = run_storage_backend_experiment(tmp_path / "storage_exp")
        assert report.conclusion
        file_obs = next(o for o in report.observations if o["backend"] == "file")
        mem_obs = next(o for o in report.observations if o["backend"] == "memory")
        assert file_obs["survives_restart"] is True
        assert file_obs["file_count"] > 0
        assert mem_obs["file_count"] == 0


class TestApprovalPolicyExperiment:
    def test_fail_run_vs_remain_interrupted(self) -> None:
        report = run_approval_policy_experiment()
        fail_obs = next(o for o in report.observations if o["policy"] == "fail_run")
        remain_obs = next(o for o in report.observations if o["policy"] == "remain_interrupted")
        assert fail_obs["status_after_deny"] == "failed"
        assert fail_obs["can_retry_resume"] is False
        assert remain_obs["status_after_deny"] == "interrupted"
        assert remain_obs["can_retry_resume"] is True
        assert fail_obs["error_code"] == "APPROVAL_DENIED"
        assert remain_obs["error_code"] == "APPROVAL_DENIED"
