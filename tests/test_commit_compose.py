from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from conventional_git.commit.compose import build_message
from conventional_git.commit.compose import normalize_description
from conventional_git.commit.rules import validate_message

if TYPE_CHECKING:
    from typing import Final

NORMALIZE_CASES: Final[list[tuple[str | None, str]]] = [
    ("Add OAuth login.", "add OAuth login"),
    ("  add login  ", "add login"),
    ("", "update implementation"),
    (None, "update implementation"),
    ("...", "update implementation"),
]


@pytest.mark.parametrize(("raw", "expected"), NORMALIZE_CASES)
def test_normalize_description_matches_expected(raw: str | None, expected: str) -> None:
    # Arrange
    # Act
    normalized = normalize_description(raw)
    # Assert
    assert normalized == expected


def test_build_message_renders_a_bare_title_without_a_body() -> None:
    # Arrange
    # Act
    message = build_message("feat", None, "add oauth login", (), breaking=False)
    # Assert
    assert message == "feat: add oauth login"


def test_build_message_renders_a_scope_and_bulleted_body() -> None:
    # Arrange
    body_lines = ["retry once", "- log the failure"]
    # Act
    message = build_message("fix", "auth", "handle expired tokens", body_lines, breaking=False)
    # Assert
    assert message == "fix(auth): handle expired tokens\n\n- retry once\n- log the failure"


def test_build_message_renders_a_breaking_footer() -> None:
    # Arrange
    # Act
    message = build_message("feat", "api", "drop the v1 endpoint", (), breaking=True)
    # Assert
    assert message == "feat(api)!: drop the v1 endpoint\n\n\n\nBREAKING CHANGE: drop the v1 endpoint"


ROUND_TRIP_CASES: Final[list[tuple[str, str | None, str, tuple[str, ...], bool]]] = [
    ("feat", None, "add oauth login", (), False),
    ("fix", "auth", "handle expired tokens", ("retry once", "log the failure"), False),
    ("feat", "api", "drop the v1 endpoint", ("migrate callers first",), True),
]


@pytest.mark.parametrize(("commit_type", "scope", "description", "body_lines", "breaking"), ROUND_TRIP_CASES)
def test_build_message_output_always_passes_validate_message(
    commit_type: str,
    scope: str | None,
    description: str,
    body_lines: tuple[str, ...],
    *,
    breaking: bool,
) -> None:
    # Arrange
    message = build_message(commit_type, scope, description, body_lines, breaking=breaking)
    # Act
    report = validate_message(message)
    # Assert
    assert report.valid, report.violations
