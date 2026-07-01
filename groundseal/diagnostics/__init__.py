"""Operator diagnostics and human-readable run summaries."""

from __future__ import annotations

from typing import Protocol

from groundseal.diagnostics.report import (
    DiagnosticReport,
    RunSummary,
    build_diagnostic_report,
    build_run_summary,
    format_run_summary_text,
)


class RunReader(Protocol):
    def get_run(self, run_id: str): ...
    def list_checkpoints(self, run_id: str): ...


__all__ = [
    "DiagnosticReport",
    "RunSummary",
    "RunReader",
    "build_diagnostic_report",
    "build_run_summary",
    "format_run_summary_text",
]
