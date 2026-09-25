from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from conventional_git.branch.rules import validate_name
from conventional_git.commit.rules import validate_message
from conventional_git.violations import ViolationCode

if TYPE_CHECKING:
    from typing import Final

_COMMIT_CASES: Final[dict[ViolationCode, str]] = {
    ViolationCode.COMMIT_EMPTY: "",
    ViolationCode.COMMIT_HEADER_FORMAT: "not a conventional header",
    ViolationCode.COMMIT_TYPE: "banana: add login",
    ViolationCode.COMMIT_DESCRIPTION_FORMAT: "feat: Add login",
    ViolationCode.COMMIT_DESCRIPTION_TRAILING_PERIOD: "feat: add login.",
    ViolationCode.COMMIT_TITLE_LENGTH: f"feat: {'x' * 200}",
    ViolationCode.COMMIT_BODY_LINE_LENGTH: f"feat: add login\n\n- {'x' * 200}",
    ViolationCode.COMMIT_BODY_BULLET: "feat: add login\n\nnot a bullet line",
    ViolationCode.COMMIT_MESSAGE_BYTES: f"feat: add login\n\n- {'x' * 2100}",
    ViolationCode.COMMIT_BREAKING_FOOTER: "feat!: drop v1 endpoints",
    ViolationCode.COMMIT_ATTRIBUTION: "feat: add login\n\nCo-Authored-By: Jane Doe <jane@example.com>",
}

_BRANCH_CASES: Final[dict[ViolationCode, str]] = {
    ViolationCode.BRANCH_FORMAT: "Bad_Name",
    ViolationCode.BRANCH_TYPE: "banana/add-login",
    ViolationCode.BRANCH_DESCRIPTION_LENGTH: f"feature/{'a' * 80}",
}


@pytest.mark.parametrize(("code", "message"), _COMMIT_CASES.items(), ids=[code.value for code in _COMMIT_CASES])
def test_commit_violation_codes_are_reachable(code: ViolationCode, message: str) -> None:
    # Arrange
    # Act
    report = validate_message(message)
    # Assert
    assert any(v.code == code for v in report.violations)


@pytest.mark.parametrize(("code", "name"), _BRANCH_CASES.items(), ids=[code.value for code in _BRANCH_CASES])
def test_branch_violation_codes_are_reachable(code: ViolationCode, name: str) -> None:
    # Arrange
    # Act
    report = validate_name(name)
    # Assert
    assert any(v.code == code for v in report.violations)


# `branch.description-empty` (rules.py's `if not description:` check) can never fire: the
# branch-name regex's description group requires at least one alphanumeric character, so an
# empty description always fails to parse first and yields `branch.format` instead.
_DEAD_CODES: Final[frozenset[ViolationCode]] = frozenset({ViolationCode.BRANCH_DESCRIPTION_EMPTY})


def test_every_violation_code_is_exercised_or_explicitly_noted_as_dead() -> None:
    # Arrange
    dead_codes = _DEAD_CODES
    exercised = set(_COMMIT_CASES) | set(_BRANCH_CASES)
    # Act
    # Assert
    assert exercised | dead_codes == set(ViolationCode)
