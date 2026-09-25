from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING

from conventional_git import generation
from conventional_git.generation.heuristic import HeuristicProvider
from conventional_git.generation.protocol import ProviderError
from conventional_git.mcp import server

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Final

    import pytest


_FAILURE_MESSAGE: Final[str] = "jev provider failed: connection refused"


class _FailingProvider:
    name = "jev"

    @staticmethod
    def suggest(
        diff: str,
        *,
        changed_paths: tuple[str, ...] = (),
        types: Mapping[str, str] | None = None,
    ) -> None:
        del diff, changed_paths, types
        raise ProviderError(_FAILURE_MESSAGE)


def test_suggest_commit_message_falls_back_to_heuristic_on_a_provider_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    monkeypatch.setattr(generation, "enable_optional_providers", lambda: None)
    monkeypatch.setattr(generation, "available_providers", lambda: ("jev", "heuristic"))
    providers = {"jev": _FailingProvider(), "heuristic": HeuristicProvider()}
    monkeypatch.setattr(generation, "get_provider", providers.get)
    diff = "diff --git a/src/foo.py b/src/foo.py\n--- a/src/foo.py\n+++ b/src/foo.py\n@@ -1 +1 @@\n-a\n+b\n"
    expected_suggestion = HeuristicProvider().suggest(diff, changed_paths=("src/foo.py",))
    # Act
    result = server.suggest_commit_message(diff, changed_paths=["src/foo.py"])
    # Assert
    assert result == {
        "provider": "heuristic",
        "suggestion": asdict(expected_suggestion) if expected_suggestion else None,
        "warning": _FAILURE_MESSAGE,
    }
