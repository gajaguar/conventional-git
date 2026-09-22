from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Final

from conventional_kit.commit.vocabulary import load_from_csv
from conventional_kit.config import Config
from conventional_kit.helpers import strip_attribution
from conventional_kit.violations import Severity
from conventional_kit.violations import Violation

_STRIPPED_CLAUDE: Final[str] = (
    "feat: add login\n\n- bullet one\nCo-Authored-By: Claude <noreply@anthropic.com>\n- bullet two"
)
_STRIPPED_SIGNED_OFF: Final[str] = "feat: add login\n\n- bullet one\nSigned-off-by: bot@example.com"
_CUSTOM_CONFIG: Final[Config] = Config(
    extra_attribution_patterns=("Signed-off-by",),
    commit_type_overrides=(),
    branch_type_overrides=(),
    branch_trunk_overrides=(),
)


def test_strip_attribution_removes_claude_line() -> None:
    # Arrange
    # Act
    cleaned = strip_attribution(_STRIPPED_CLAUDE)
    # Assert
    assert cleaned == ["feat: add login", "- bullet one", "- bullet two"]


def test_strip_attribution_with_custom_config() -> None:
    # Arrange
    # Act
    cleaned = strip_attribution(_STRIPPED_SIGNED_OFF, config=_CUSTOM_CONFIG)
    # Assert
    assert cleaned == ["feat: add login", "- bullet one"]


def test_vocabulary_load_from_csv() -> None:
    # Arrange
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "types.csv"
        path.write_text("type,when_to_use\nfoo,bar\nbaz,qux\n", encoding="utf-8")
        # Act
        types = load_from_csv(path)
        # Assert
        assert types == frozenset({"foo", "baz"})


def test_violation_dataclass_round_trip() -> None:
    # Arrange
    violation = Violation(
        code="x",
        field="y",
        message="m",
        fix_hint="h",
        severity=Severity.WARNING,
    )
    # Act
    data = violation.to_dict()
    # Assert
    assert data == {
        "code": "x",
        "field": "y",
        "message": "m",
        "fix_hint": "h",
        "severity": "warning",
    }
