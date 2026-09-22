from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from gitlint.rules import CommitMessageBody
from gitlint.rules import CommitRule
from gitlint.rules import LineRule
from gitlint.rules import RuleViolation

from conventional_git.commit import grammar as commit_grammar
from conventional_git.commit import rules as commit_rules
from conventional_git.violations import Severity

if TYPE_CHECKING:
    from gitlint.git import GitCommit


def _to_gitlint(message: str) -> list[RuleViolation]:
    report = commit_rules.validate_message(message)
    violations: list[RuleViolation] = []
    for violation in report.violations:
        label = "WARNING" if violation.severity is Severity.WARNING else "ERROR"
        violations.append(
            RuleViolation(
                rule_id=f"conventional-git/{violation.code}",
                message=f"{label}: {violation.field}: {violation.message}",
                content=violation.fix_hint,
            )
        )
    return violations


class ConventionalCommitHeaderRule(CommitRule):  # type: ignore[misc]
    name = "conventional-git-header"
    id = "CG1"

    def validate(self, commit: GitCommit) -> list[RuleViolation]:
        return _to_gitlint(commit.message.original)


class ConventionalCommitBodyLineRule(LineRule):  # type: ignore[misc]
    name = "conventional-git-body-line"
    id = "CG2"
    target = CommitMessageBody

    def validate(self, line: str, commit: GitCommit) -> list[RuleViolation] | None:
        del commit
        body_line_max = commit_rules.body_line_max()
        if len(line) > body_line_max:
            return [
                RuleViolation(
                    rule_id="conventional-git/body-line-length",
                    message=(f"ERROR: body: Body line exceeds {body_line_max} characters ({len(line)})"),
                    content=f"Wrap or shorten the line to at most {body_line_max} characters",
                )
            ]
        return None


def rule_classes() -> list[type[Any]]:
    return [ConventionalCommitHeaderRule, ConventionalCommitBodyLineRule]


__all__ = [
    "ConventionalCommitBodyLineRule",
    "ConventionalCommitHeaderRule",
    "commit_grammar",
    "rule_classes",
]
