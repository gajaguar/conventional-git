from __future__ import annotations

from typing import TYPE_CHECKING

from gitlint.git import GitContext

from conventional_git.adapters import gitlint_rules

if TYPE_CHECKING:
    from gitlint.git import GitCommit


def _commit(message: str) -> GitCommit:
    return GitContext.from_commit_msg(message).commits[-1]


def test_header_rule_accepts_a_valid_conventional_commit() -> None:
    # Arrange
    rule = gitlint_rules.ConventionalCommitHeaderRule()
    commit = _commit("feat: add login")
    # Act
    violations = rule.validate(commit)
    # Assert
    assert violations == []


def test_header_rule_reports_an_invalid_conventional_commit() -> None:
    # Arrange
    rule = gitlint_rules.ConventionalCommitHeaderRule()
    commit = _commit("added login")
    # Act
    violations = rule.validate(commit)
    # Assert
    assert violations
    assert all(v.rule_id.startswith("conventional-git/") for v in violations)


def test_body_line_rule_accepts_a_short_line() -> None:
    # Arrange
    rule = gitlint_rules.ConventionalCommitBodyLineRule()
    commit = _commit("feat: add login\n\nshort body line")
    # Act
    violation = rule.validate("short body line", commit)
    # Assert
    assert violation is None


def test_body_line_rule_reports_a_line_over_the_limit() -> None:
    # Arrange
    rule = gitlint_rules.ConventionalCommitBodyLineRule()
    long_line = "x" * (gitlint_rules.commit_rules.body_line_max() + 1)
    commit = _commit(f"feat: add login\n\n{long_line}")
    # Act
    violations = rule.validate(long_line, commit)
    # Assert
    assert violations is not None
    assert violations[0].rule_id == "conventional-git/body-line-length"
