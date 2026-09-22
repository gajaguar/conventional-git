from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Final

import pytest

from conventional_git.branch.rules import build_branch_name
from conventional_git.branch.rules import default_description
from conventional_git.branch.rules import normalize_description
from conventional_git.branch.rules import validate_name
from conventional_git.branch.vocabulary import merge_trunks

if TYPE_CHECKING:
    from pathlib import Path

DESCRIPTION_CASES: Final[list[tuple[str, str]]] = [
    ("Add OAuth login", "add-oauth-login"),
    ("v1.2.0", "v1.2.0"),
    ("new--login", "new-login"),
    ("-new-login-", "new-login"),
    ("Café Sync", "cafe-sync"),
    ("a" * 80, "a" * 75),
]


@pytest.mark.parametrize(("raw", "expected"), DESCRIPTION_CASES)
def test_normalize_description_matches_expected(raw: str, expected: str) -> None:
    # Arrange
    # Act
    normalized = normalize_description(raw)
    # Assert
    assert normalized == expected


def test_normalize_description_defaults_when_empty() -> None:
    # Arrange
    # Act
    normalized = normalize_description("")
    # Assert
    assert normalized == default_description()


def test_build_branch_name_joins_type_and_description() -> None:
    # Arrange
    # Act
    name = build_branch_name("feature", "add-login")
    # Assert
    assert name == "feature/add-login"


def test_validate_name_accepts_known_type() -> None:
    # Arrange
    # Act
    report = validate_name("feature/add-login")
    # Assert
    assert report.valid


def test_validate_name_rejects_unknown_type() -> None:
    # Arrange
    # Act
    report = validate_name("banana/add-login")
    # Assert
    assert not report.valid
    assert any(v.code == "branch.type" for v in report.violations)


def test_validate_name_rejects_bad_format() -> None:
    # Arrange
    # Act
    report = validate_name("Bad_Name")
    # Assert
    assert not report.valid
    assert any(v.code == "branch.format" for v in report.violations)


def test_validate_name_accepts_custom_type_overrides(tmp_path: Path) -> None:
    # Arrange
    reference = tmp_path / "branch-types.csv"
    reference.write_text("type,when_to_use\nfoo,bar\n", encoding="utf-8")
    allowed = frozenset({"foo"})
    # Act
    report = validate_name("foo/add-login", allowed_types=allowed)
    # Assert
    assert report.valid


def test_validate_name_rejects_unknown_type_with_overrides(tmp_path: Path) -> None:
    # Arrange
    reference = tmp_path / "branch-types.csv"
    reference.write_text("type,when_to_use\nfoo,bar\n", encoding="utf-8")
    allowed = frozenset({"foo"})
    # Act
    report = validate_name("banana/add-login", allowed_types=allowed)
    # Assert
    assert not report.valid
    assert any(v.code == "branch.type" for v in report.violations)


def test_validate_name_requires_a_value() -> None:
    # Arrange
    # Act
    report = validate_name("")
    # Assert
    assert not report.valid
    assert any(v.code == "branch.format" for v in report.violations)


@pytest.mark.parametrize("trunk", ["main", "master", "develop"])
def test_validate_name_accepts_default_trunk_branches(trunk: str) -> None:
    # Arrange
    # Act
    report = validate_name(trunk)
    # Assert
    assert report.valid


def test_validate_name_rejects_trunk_lookalike() -> None:
    # Arrange
    # Act
    report = validate_name("mainline")
    # Assert
    assert not report.valid
    assert any(v.code == "branch.format" for v in report.violations)


def test_validate_name_respects_trunk_branches_override() -> None:
    # Arrange
    trunks = frozenset({"trunk"})
    # Act
    main_report = validate_name("main", trunk_branches=trunks)
    trunk_report = validate_name("trunk", trunk_branches=trunks)
    # Assert
    assert not main_report.valid
    assert trunk_report.valid


def test_merge_trunks_adds_to_defaults(tmp_path: Path) -> None:
    # Arrange
    reference = tmp_path / "branch-trunks.csv"
    reference.write_text("name,when_to_use\npython,Permanent language layer branch\n", encoding="utf-8")
    # Act
    trunks = merge_trunks((reference,))
    # Assert
    assert {"main", "master", "develop", "python"} <= trunks


def test_merge_trunks_skips_missing_paths(tmp_path: Path) -> None:
    # Arrange
    missing = tmp_path / "does-not-exist.csv"
    # Act
    trunks = merge_trunks((missing,))
    # Assert
    assert trunks == {"main", "master", "develop"}
