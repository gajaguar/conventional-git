from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import Self

import pytest

from conventional_git.generation.protocol import MissingCredentialsError
from conventional_git.generation.typesafe import JevProvider

if TYPE_CHECKING:
    from typing import Final


@dataclass
class _FakeChoiceAnswer:
    choice: str
    confidence: float = 0.9


@dataclass
class _FakeNoulAnswer:
    noul: float


@dataclass
class _FakeResponse:
    choices: dict[str, _FakeChoiceAnswer]
    nouls: dict[str, _FakeNoulAnswer]


class _FakeClient:
    def __init__(self, response: _FakeResponse) -> None:
        self._response = response
        self.last_questions: dict[str, Any] | None = None

    def system_one(self, *, state: object, questions: dict[str, Any]) -> _FakeResponse:
        del state
        self.last_questions = questions
        return self._response

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc_info: object) -> None:
        del exc_info


def _provider(response: _FakeResponse) -> JevProvider:
    return JevProvider(client_factory=lambda: _FakeClient(response))


_MISSING_CREDENTIALS_MESSAGE: Final[str] = "no key"


def _raise_missing_credentials() -> _FakeClient:
    raise MissingCredentialsError(_MISSING_CREDENTIALS_MESSAGE)


def test_suggest_maps_choice_and_noul_answers_onto_a_commit_suggestion() -> None:
    # Arrange
    response = _FakeResponse(
        choices={
            "type": _FakeChoiceAnswer(choice="fix", confidence=0.87),
            "scope": _FakeChoiceAnswer(choice="cli"),
            "description": _FakeChoiceAnswer(choice="fix the login flow"),
        },
        nouls={"breaking": _FakeNoulAnswer(noul=0.1)},
    )
    provider = _provider(response)
    # Act
    suggestion = provider.suggest("diff", changed_paths=("src/conventional_git/cli/create.py",))
    # Assert
    assert suggestion is not None
    assert suggestion.type == "fix"
    assert suggestion.scope == "cli"
    assert suggestion.description == "fix the login flow"
    assert suggestion.confidence == pytest.approx(0.87)
    assert suggestion.breaking is False


def test_suggest_maps_none_scope_choice_to_an_empty_scope() -> None:
    # Arrange
    response = _FakeResponse(
        choices={
            "type": _FakeChoiceAnswer(choice="chore"),
            "scope": _FakeChoiceAnswer(choice="none"),
            "description": _FakeChoiceAnswer(choice="update files"),
        },
        nouls={"breaking": _FakeNoulAnswer(noul=0.6)},
    )
    provider = _provider(response)
    # Act
    suggestion = provider.suggest("diff", changed_paths=("README.md", "src/foo.py"))
    # Assert
    assert suggestion is not None
    assert not suggestion.scope
    assert suggestion.breaking is True


def test_suggest_falls_back_to_the_heuristic_type_for_an_unknown_choice() -> None:
    # Arrange
    response = _FakeResponse(
        choices={
            "type": _FakeChoiceAnswer(choice="not-a-real-type"),
            "scope": _FakeChoiceAnswer(choice="none"),
            "description": _FakeChoiceAnswer(choice="update files"),
        },
        nouls={"breaking": _FakeNoulAnswer(noul=0.0)},
    )
    provider = _provider(response)
    # Act
    suggestion = provider.suggest("diff", changed_paths=("tests/test_foo.py",))
    # Assert
    assert suggestion is not None
    assert suggestion.type == "test"


def test_suggest_returns_none_for_empty_input() -> None:
    # Arrange
    provider = _provider(_FakeResponse(choices={}, nouls={}))
    # Act
    suggestion = provider.suggest("")
    # Assert
    assert suggestion is None


def test_suggest_raises_missing_credentials_when_the_client_factory_does() -> None:
    # Arrange
    provider = JevProvider(client_factory=_raise_missing_credentials)
    # Act
    # Assert
    with pytest.raises(MissingCredentialsError):
        provider.suggest("diff", changed_paths=("src/foo.py",))
