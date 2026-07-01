#!/usr/bin/env python3
"""Run Phase 8 comparative experiments and print JSON report."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from groundseal.evaluation.experiments import (
    run_approval_policy_experiment,
    run_storage_backend_experiment,
)


def main() -> int:
    tmp = Path("/tmp/groundseal_exp_cli")
    reports = {
        "storage_backend": run_storage_backend_experiment(tmp).to_dict(),
        "approval_policy": run_approval_policy_experiment().to_dict(),
    }
    print(json.dumps(reports, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
