"""Structured errors for fail-closed behavior."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GroundSealError(Exception):
    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"
