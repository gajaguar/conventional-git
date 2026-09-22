from __future__ import annotations

from typing import Any

from gitlint.rules import CommitMessage  # pyright: ignore[reportAttributeAccessIssue]
from gitlint.rules import LineRule
from gitlint.rules import RuleViolation
from gitlint.rules import UserRule  # pyright: ignore[reportAttributeAccessIssue]

from conventional_kit.commit import grammar as commit_grammar
from conventional_kit.commit import rules as commit_rules
from conventional_kit.violations import Severity


def _to_gitlint(message: str) -> list[Any]:
    report = commit_rules.validate_message(message)
    violations: list[Any] = []
    for violation in report.violations:
        severity = "W" if violation.severity is Severity.WARNING else "E"
        violations.append(
            RuleViolation(
                rule_id=f"conventional-kit/{violation.code}",
                severity=severity,  # pyright: ignore[reportCallIssue]
                message=f"{violation.field}: {violation.message}",
                content=violation.fix_hint,
            )
        )
    return violations


class ConventionalCommitHeaderRule(UserRule):  # type: ignore[misc]
    name = "conventional-kit-header"

    def validate(self, commit: CommitMessage) -> list[Any]:
        return _to_gitlint(commit.original_commit_message)


class ConventionalCommitBodyLineRule(LineRule):  # type: ignore[misc]
    name = "conventional-kit-body-line"

    def validate_line(self, line: str, _commit: CommitMessage) -> Any:
        _ = _commit
        body_line_max = commit_rules.body_line_max()
        if len(line) > body_line_max:
            return RuleViolation(
                rule_id="conventional-kit/body-line-length",
                severity="E",  # pyright: ignore[reportCallIssue]
                message=(f"body: Body line exceeds {body_line_max} characters ({len(line)})"),
                content=f"Wrap or shorten the line to at most {body_line_max} characters",
            )
        return None


def rule_classes() -> list[type[Any]]:
    return [ConventionalCommitHeaderRule, ConventionalCommitBodyLineRule]


__all__ = [
    "ConventionalCommitBodyLineRule",
    "ConventionalCommitHeaderRule",
    "commit_grammar",
    "rule_classes",
]
