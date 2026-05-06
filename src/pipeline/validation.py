"""共有バリデーション型。複数の pipeline モジュールから使う。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ValidationIssue:
    code: str
    field: str
    message: str
    severity: str = "error"  # "error" or "warning"

    def to_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "field": self.field,
            "message": self.message,
            "severity": self.severity,
        }
