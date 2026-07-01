#!/usr/bin/env python3
"""Run evaluation baseline and optionally compare or ratchet."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from groundseal.evaluation import compare_to_baseline, run_evaluation

DEFAULT_BASELINE = Path(__file__).resolve().parent.parent / "eval" / "baseline.json"
REPORT_DIR = Path(__file__).resolve().parent.parent / "reports" / "generated"


def main() -> int:
    parser = argparse.ArgumentParser(description="GroundSeal evaluation baseline runner")
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--ratchet", action="store_true", help="Update baseline if improved or initial")
    parser.add_argument("--reason", type=str, default="", help="Required explanation when ratcheting")
    parser.add_argument("--report", action="store_true", help="Write JSON report to reports/generated/")
    args = parser.parse_args()

    report = run_evaluation()
    comparison = compare_to_baseline(
        report,
        args.baseline,
        ratchet=args.ratchet,
        reason=args.reason or None,
    )

    if args.report:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        out = REPORT_DIR / "eval_report.json"
        payload = {"report": report.to_dict(), "comparison": comparison}
        out.write_text(json.dumps(payload, indent=2) + "\n")
        print(f"Report written to {out}")

    print(json.dumps(comparison, indent=2))

    if comparison["status"] == "regression":
        return 1
    if report.failed > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
