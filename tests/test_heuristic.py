from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from conventional_git.generation.heuristic import HeuristicProvider

if TYPE_CHECKING:
    from typing import Final

CASES: Final[list[tuple[tuple[str, ...], str]]] = [
    (("tests/test_foo.py",), "test"),
    (("tests/sub/test_bar.py",), "test"),
    (("docs/index.md",), "docs"),
    (("README.md",), "docs"),
    (("pyproject.toml",), "build"),
    (("uv.lock",), "build"),
    (("Makefile",), "build"),
    ((".github/workflows/ci.yml",), "ci"),
    (("src/agent_kit/vcs/commit.py",), "chore"),
]


@pytest.mark.parametrize(("paths", "expected_type"), CASES)
def test_heuristic_infers_type_from_paths(paths: tuple[str, ...], expected_type: str) -> None:
    # Arrange
    provider = HeuristicProvider()
    # Act
    suggestion = provider.suggest(diff="", changed_paths=paths)
    # Assert
    assert suggestion is not None
    assert suggestion.type == expected_type


def test_heuristic_returns_none_for_empty_input() -> None:
    # Arrange
    provider = HeuristicProvider()
    # Act
    suggestion = provider.suggest(diff="")
    # Assert
    assert suggestion is None


def test_heuristic_extracts_paths_from_diff() -> None:
    # Arrange
    diff = "diff --git a/src/foo.py b/src/foo.py\n--- a/src/foo.py\n+++ b/src/foo.py\n@@ -1 +1 @@\n-old\n+new\n"
    provider = HeuristicProvider()
    # Act
    suggestion = provider.suggest(diff=diff)
    # Assert
    assert suggestion is not None
    assert suggestion.type == "chore"


def test_heuristic_normalizes_description_case() -> None:
    # Arrange
    provider = HeuristicProvider()
    # Act
    suggestion = provider.suggest(diff="", changed_paths=("src/Agent.py",))
    # Assert
    assert suggestion is not None
    assert suggestion.description.startswith(("update ", "apply "))


def test_heuristic_handles_dev_null_paths() -> None:
    # Arrange
    diff = "diff --git a/old.py b/old.py\n--- a/old.py\n+++ b/dev/null\n"
    provider = HeuristicProvider()
    # Act
    suggestion = provider.suggest(diff=diff)
    # Assert
    assert suggestion is not None
