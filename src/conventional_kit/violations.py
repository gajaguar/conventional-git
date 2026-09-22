from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True, slots=True)
class Violation:
    code: str
    field: str
    message: str
    fix_hint: str
    severity: Severity = Severity.ERROR

    def to_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "field": self.field,
            "message": self.message,
            "fix_hint": self.fix_hint,
            "severity": self.severity.value,
        }


@dataclass(frozen=True, slots=True)
class Report:
    violations: tuple[Violation, ...]

    @property
    def valid(self) -> bool:
        return not any(v.severity is Severity.ERROR for v in self.violations)

    @property
    def errors(self) -> tuple[Violation, ...]:
        return tuple(v for v in self.violations if v.severity is Severity.ERROR)

    @property
    def warnings(self) -> tuple[Violation, ...]:
        return tuple(v for v in self.violations if v.severity is Severity.WARNING)

    def to_dict(self) -> dict[str, object]:
        return {
            "valid": self.valid,
            "violations": [v.to_dict() for v in self.violations],
        }

    @classmethod
    def empty(cls) -> Report:
        return cls(violations=())

    @classmethod
    def from_violations(cls, *violations: Violation) -> Report:
        return cls(violations=tuple(violations))

    def __bool__(self) -> bool:
        return self.valid
