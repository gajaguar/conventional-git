from __future__ import annotations

import pytest

from conventional_git.commit.rules import validate_message
from conventional_git.violations import Severity


def test_valid_commit_message_passes() -> None:
    # Arrange
    # Act
    report = validate_message("feat(auth): add oauth login")
    # Assert
    assert report.valid


def test_unknown_type_yields_violation() -> None:
    # Arrange
    # Act
    report = validate_message("banana: add login")
    # Assert
    assert not report.valid
    assert any(v.code == "commit.type" for v in report.violations)


def test_trailing_period_yields_warning() -> None:
    # Arrange
    # Act
    report = validate_message("feat: add login.")
    # Assert
    assert report.valid
    assert any(v.severity is Severity.WARNING for v in report.warnings)


def test_breaking_marker_requires_footer() -> None:
    # Arrange
    # Act
    report = validate_message("feat(api)!: drop v1 endpoints")
    # Assert
    assert not report.valid
    assert any(v.code == "commit.breaking-footer" for v in report.violations)


@pytest.mark.parametrize(
    ("footer", "expected_violation"),
    [
        ("BREAKING CHANGE: drop v1", None),
        ("BREAKING-CHANGE: drop v1", None),
        ("- see BREAKING CHANGE: drop v1", "commit.breaking-footer"),
        ("  BREAKING CHANGE: drop v1", "commit.breaking-footer"),
        ("BREAKING CHANGE:", "commit.breaking-footer"),
        ("BREAKING CHANGE:   ", "commit.breaking-footer"),
        ("BREAKING CHANGE:\ndrop v1", "commit.breaking-footer"),
    ],
)
def test_breaking_footer_requires_line_start_and_nonblank_same_line_value(
    footer: str, expected_violation: str | None
) -> None:
    # Arrange
    message = f"feat!: x\n\n{footer}"
    # Act
    report = validate_message(message)
    # Assert
    violation_codes = {violation.code for violation in report.violations}
    if expected_violation is None:
        assert "commit.breaking-footer" not in violation_codes
    else:
        assert expected_violation in violation_codes


def test_title_length_violation() -> None:
    # Arrange
    long_desc = "x" * 200
    # Act
    report = validate_message(f"feat: {long_desc}")
    # Assert
    assert not report.valid
    assert any(v.code == "commit.title-length" for v in report.violations)


def test_empty_message_violation() -> None:
    # Arrange
    # Act
    report = validate_message("")
    # Assert
    assert not report.valid
    assert any(v.code == "commit.empty" for v in report.violations)


def test_co_authored_by_trailer_yields_violation() -> None:
    # Arrange
    message = "feat(python): add python language layer\n\nCo-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>\n"
    # Act
    report = validate_message(message)
    # Assert
    assert not report.valid
    assert any(v.code == "commit.attribution" for v in report.violations)


def test_human_co_authored_by_trailer_yields_violation() -> None:
    # Arrange
    message = "feat: pair on login\n\n- bullet one\nCo-Authored-By: Jane Doe <jane@example.com>"
    # Act
    report = validate_message(message)
    # Assert
    assert not report.valid
    assert any(v.code == "commit.attribution" for v in report.violations)


def test_generated_with_emoji_line_yields_violation() -> None:
    # Arrange
    message = (
        "feat: add login\n\n- bullet one\n\U0001f916 Generated with [Claude Code](https://claude.com/claude-code)"
    )
    # Act
    report = validate_message(message)
    # Assert
    assert not report.valid
    assert any(v.code == "commit.attribution" for v in report.violations)


def test_bare_mention_of_tool_name_is_allowed() -> None:
    # Arrange
    # Act
    report = validate_message("feat(plugin): add claude plugin manifest")
    # Assert
    assert report.valid


def test_extra_attribution_pattern_is_rejected() -> None:
    # Arrange
    message = "feat: add login\n\n- bullet one\nSigned-off-by: bot@example.com"
    # Act
    report = validate_message(message, attribution_patterns=("Signed-off-by",))
    # Assert
    assert not report.valid
    assert any(v.code == "commit.attribution" for v in report.violations)
