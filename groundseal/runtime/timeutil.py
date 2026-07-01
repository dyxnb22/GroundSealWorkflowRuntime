"""Clock helpers — inject clock in tests for determinism."""

from __future__ import annotations

from datetime import UTC, datetime

DEFAULT_TEST_CLOCK = "2026-07-01T00:00:00Z"


def now(clock: str | None) -> str:
    if clock is not None:
        return clock
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
