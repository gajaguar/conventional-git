from __future__ import annotations

from typing import TYPE_CHECKING

from conventional_git.generation import protocol
from conventional_git.generation.heuristic import HeuristicProvider
from conventional_git.generation.protocol import CommitSuggestion
from conventional_git.generation.protocol import ProviderError
from conventional_git.generation.protocol import suggest

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Final

    import pytest

_SAMPLE_DIFF: Final[str] = (
    "diff --git a/src/foo.py b/src/foo.py\n--- a/src/foo.py\n+++ b/src/foo.py\n@@ -1 +1 @@\n-a\n+b\n"
)
_FAILURE_MESSAGE: Final[str] = "jev provider failed: connection refused"


class _FailingProvider:
    name = "jev"

    @staticmethod
    def suggest(
        diff: str,
        *,
        changed_paths: tuple[str, ...] = (),
        types: Mapping[str, str] | None = None,
    ) -> CommitSuggestion | None:
        del diff, changed_paths, types
        raise ProviderError(_FAILURE_MESSAGE)


def test_suggest_returns_an_error_for_an_unknown_preferred_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    monkeypatch.setattr(protocol, "enable_optional_providers", lambda: None)
    monkeypatch.setattr(protocol, "available_providers", lambda: ("heuristic",))
    monkeypatch.setattr(protocol, "get_provider", lambda _name: None)
    # Act
    result = suggest(_SAMPLE_DIFF, preferred="bogus")
    # Assert
    assert result.error == "Unknown provider 'bogus'. Available: heuristic"
    assert result.provider is None
    assert result.suggestion is None


def test_suggest_does_not_fall_back_when_the_preferred_provider_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    monkeypatch.setattr(protocol, "enable_optional_providers", lambda: None)
    monkeypatch.setattr(protocol, "available_providers", lambda: ("jev", "heuristic"))
    providers = {"jev": _FailingProvider(), "heuristic": HeuristicProvider()}
    monkeypatch.setattr(protocol, "get_provider", providers.get)
    # Act
    result = suggest(_SAMPLE_DIFF, preferred="jev")
    # Assert
    assert result.error == _FAILURE_MESSAGE
    assert result.suggestion is None
    assert result.warning is None


def test_suggest_falls_back_to_heuristic_when_no_provider_was_requested(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    monkeypatch.setattr(protocol, "enable_optional_providers", lambda: None)
    monkeypatch.setattr(protocol, "available_providers", lambda: ("jev", "heuristic"))
    providers = {"jev": _FailingProvider(), "heuristic": HeuristicProvider()}
    monkeypatch.setattr(protocol, "get_provider", providers.get)
    expected = HeuristicProvider().suggest(_SAMPLE_DIFF, changed_paths=("src/foo.py",))
    # Act
    result = suggest(_SAMPLE_DIFF, changed_paths=("src/foo.py",))
    # Assert
    assert result.provider == "heuristic"
    assert result.suggestion == expected
    assert result.warning == _FAILURE_MESSAGE


def test_suggest_returns_the_preferred_providers_suggestion_on_success(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    monkeypatch.setattr(protocol, "enable_optional_providers", lambda: None)
    monkeypatch.setattr(protocol, "available_providers", lambda: ("heuristic",))
    monkeypatch.setattr(protocol, "get_provider", {"heuristic": HeuristicProvider()}.get)
    expected = HeuristicProvider().suggest(_SAMPLE_DIFF, changed_paths=("src/foo.py",))
    # Act
    result = suggest(_SAMPLE_DIFF, changed_paths=("src/foo.py",), preferred="heuristic")
    # Assert
    assert result == protocol.SuggestionResult(provider="heuristic", suggestion=expected)
