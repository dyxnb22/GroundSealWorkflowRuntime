"""Evaluation baseline runner tests."""

from __future__ import annotations

import json
from pathlib import Path

from groundseal.evaluation import compare_to_baseline, run_evaluation

BASELINE_PATH = Path(__file__).parent.parent / "eval" / "baseline.json"


class TestEvaluationBaseline:
    def test_run_evaluation_all_pass(self) -> None:
        report = run_evaluation()
        assert report.failed == 0
        assert report.passed == report.total
        assert report.metrics["categories_covered"] >= 5

    def test_compare_to_baseline_ok(self) -> None:
        report = run_evaluation()
        result = compare_to_baseline(report, BASELINE_PATH)
        assert result["status"] in ("ok", "missing_baseline", "regression")
        if result["status"] == "ok":
            assert result["current"]["passed"] >= result["baseline"]["passed"]

    def test_baseline_file_structure(self) -> None:
        assert BASELINE_PATH.exists()
        data = json.loads(BASELINE_PATH.read_text())
        assert "baseline" in data
        assert data["baseline"]["total"] >= 7
        assert data["baseline"]["pass_rate"] == 1.0
