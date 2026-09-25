from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from gitlint.config import LintConfig
from gitlint.git import GitContext
from gitlint.lint import GitLinter

from conventional_git.adapters import gitlint_rules

if TYPE_CHECKING:
    from typing import Final

    import pytest
    from gitlint.git import GitCommit
    from gitlint.rules import RuleViolation

_ADAPTER_PATH: Final[Path] = Path(gitlint_rules.__file__)


def _commit(message: str) -> GitCommit:
    return GitContext.from_commit_msg(message).commits[-1]


def _lint(message: str, *, ignore: tuple[str, ...] = (), warnings: bool = False) -> list[RuleViolation]:
    config = LintConfig()
    config.extra_path = str(_ADAPTER_PATH)
    config.ignore = list(ignore)
    if warnings:
        config.set_rule_option("CG1", "warnings", "true")
    return GitLinter(config).lint(_commit(message))


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


def test_adapter_registers_only_the_header_rule() -> None:
    # Arrange
    expected = [gitlint_rules.ConventionalCommitHeaderRule]
    # Act
    classes = gitlint_rules.rule_classes()
    # Assert
    assert classes == expected


def test_body_line_length_is_reported_once() -> None:
    # Arrange
    long_line = "- " + "x" * gitlint_rules.commit_rules.limits().body_line_max
    # Act
    violations = _lint(f"feat: add login\n\n{long_line}", ignore=gitlint_rules.RECOMMENDED_IGNORE)
    # Assert
    body_violations = [v for v in violations if v.rule_id == "conventional-git/commit.body-line-length"]
    assert len(body_violations) == 1


def test_core_warnings_do_not_fail_a_commit_by_default() -> None:
    # Arrange
    message = "feat: add login."
    # Act
    violations = _lint(message, ignore=gitlint_rules.RECOMMENDED_IGNORE)
    # Assert
    assert violations == []


def test_warnings_option_reports_the_trailing_period() -> None:
    # Arrange
    message = "feat: add login."
    # Act
    violations = _lint(message, warnings=True, ignore=gitlint_rules.RECOMMENDED_IGNORE)
    # Assert
    assert [v.rule_id for v in violations] == ["conventional-git/commit.description-trailing-period"]
    assert violations[0].message.startswith("WARNING:")


def test_warnings_option_off_drops_the_trailing_period() -> None:
    # Arrange
    message = "feat: add login."
    # Act
    violations = _lint(message, ignore=gitlint_rules.RECOMMENDED_IGNORE)
    # Assert
    assert violations == []


def test_type_overrides_from_repository_config_are_honored(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    extra_type = "wip"
    (tmp_path / "extra-types.csv").write_text(
        f"type,when_to_use\n{extra_type},work in progress\n",
        encoding="utf-8",
    )
    (tmp_path / ".conventional-git.toml").write_text(
        '[commit]\ntype_overrides = ["extra-types.csv"]\n',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    # Act
    violations = _lint("wip: try something", ignore=gitlint_rules.RECOMMENDED_IGNORE)
    # Assert
    assert violations == []


def test_attribution_patterns_from_repository_config_are_honored(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    (tmp_path / ".conventional-git.toml").write_text(
        '[commit]\nattribution_patterns = ["^Reviewed-by:"]\n',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    # Act
    violations = _lint("feat: add login\n\nReviewed-by: someone", ignore=gitlint_rules.RECOMMENDED_IGNORE)
    # Assert
    assert [v.rule_id for v in violations] == ["conventional-git/commit.attribution"]


def test_recommended_ignore_leaves_a_valid_message_clean() -> None:
    # Arrange
    messages = ("feat: add login", "feat: add login\n\n- a proper bullet body line")
    # Act
    violations = [_lint(message, ignore=gitlint_rules.RECOMMENDED_IGNORE) for message in messages]
    # Assert
    assert violations == [[], []]
