from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import Self

import pytest
from typesafe_sdk import TypeSafeAPIConnectionError
from typesafe_sdk import TypeSafeAuthenticationError

from conventional_git.generation.protocol import MissingCredentialsError
from conventional_git.generation.protocol import ProviderError
from conventional_git.generation.typesafe import JevProvider

if TYPE_CHECKING:
    from collections.abc import Callable
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


def _raise_connection_error() -> _FakeClient:
    message = "connection refused"
    raise TypeSafeAPIConnectionError(message)


def _raise_authentication_error() -> _FakeClient:
    body = "invalid api key"
    raise TypeSafeAuthenticationError(status=401, body=body, headers={})


@pytest.mark.parametrize("client_factory", [_raise_connection_error, _raise_authentication_error])
def test_suggest_wraps_sdk_errors_in_a_provider_error(client_factory: Callable[[], _FakeClient]) -> None:
    # Arrange
    provider = JevProvider(client_factory=client_factory)
    # Act
    # Assert
    with pytest.raises(ProviderError):
        provider.suggest("diff", changed_paths=("src/foo.py",))


_NEW_FILE_DIFF: Final[str] = (
    "diff --git a/docs/usage.md b/docs/usage.md\n"
    "new file mode 100644\n"
    "--- /dev/null\n"
    "+++ b/docs/usage.md\n"
    "@@ -0,0 +1,3 @@\n"
    "+# Usage\n"
    "+\n"
    "+See below.\n"
)

_DELETED_FILE_DIFF: Final[str] = (
    "diff --git a/docs/old.md b/docs/old.md\n"
    "deleted file mode 100644\n"
    "--- a/docs/old.md\n"
    "+++ /dev/null\n"
    "@@ -1,2 +0,0 @@\n"
    "-# Old\n"
    "-content\n"
)


def _capturing_client_factory(response: _FakeResponse, captured: list[_FakeClient]) -> Callable[[], _FakeClient]:
    def _factory() -> _FakeClient:
        client = _FakeClient(response)
        captured.append(client)
        return client

    return _factory


def test_description_candidates_offer_add_for_a_new_file_diff() -> None:
    # Arrange
    response = _FakeResponse(
        choices={
            "type": _FakeChoiceAnswer(choice="docs"),
            "scope": _FakeChoiceAnswer(choice="none"),
            "description": _FakeChoiceAnswer(choice="add usage.md"),
        },
        nouls={"breaking": _FakeNoulAnswer(noul=0.0)},
    )
    captured: list[_FakeClient] = []
    provider = JevProvider(client_factory=_capturing_client_factory(response, captured))
    # Act
    provider.suggest(_NEW_FILE_DIFF, changed_paths=("docs/usage.md",))
    # Assert
    description_criteria = captured[0].last_questions["description"].criteria
    assert "add usage.md" in description_criteria
    assert "update usage.md" not in description_criteria


def test_description_candidates_offer_remove_for_a_deleted_file_diff() -> None:
    # Arrange
    response = _FakeResponse(
        choices={
            "type": _FakeChoiceAnswer(choice="docs"),
            "scope": _FakeChoiceAnswer(choice="none"),
            "description": _FakeChoiceAnswer(choice="remove old.md"),
        },
        nouls={"breaking": _FakeNoulAnswer(noul=0.0)},
    )
    captured = []
    provider = JevProvider(client_factory=_capturing_client_factory(response, captured))
    # Act
    provider.suggest(_DELETED_FILE_DIFF, changed_paths=("docs/old.md",))
    # Assert
    description_criteria = captured[0].last_questions["description"].criteria
    assert "remove old.md" in description_criteria
    assert "update old.md" not in description_criteria


def test_scope_candidates_exclude_a_head_that_equals_a_commit_type() -> None:
    # Arrange
    response = _FakeResponse(
        choices={
            "type": _FakeChoiceAnswer(choice="docs"),
            "scope": _FakeChoiceAnswer(choice="none"),
            "description": _FakeChoiceAnswer(choice="add usage.md"),
        },
        nouls={"breaking": _FakeNoulAnswer(noul=0.0)},
    )
    captured = []
    provider = JevProvider(client_factory=_capturing_client_factory(response, captured))
    # Act
    provider.suggest(_NEW_FILE_DIFF, changed_paths=("docs/usage.md",))
    # Assert
    scope_criteria = captured[0].last_questions["scope"].criteria
    assert "docs" not in scope_criteria
    assert "none" in scope_criteria


def test_suggest_offers_configured_types_to_the_model() -> None:
    # Arrange
    response = _FakeResponse(
        choices={
            "type": _FakeChoiceAnswer(choice="wip"),
            "scope": _FakeChoiceAnswer(choice="none"),
            "description": _FakeChoiceAnswer(choice="try something"),
        },
        nouls={"breaking": _FakeNoulAnswer(noul=0.0)},
    )
    captured: list[_FakeClient] = []
    provider = JevProvider(client_factory=_capturing_client_factory(response, captured))
    types = {"wip": "Work in progress", "feat": "New feature"}
    # Act
    suggestion = provider.suggest("diff", changed_paths=("src/foo.py",), types=types)
    # Assert
    assert "wip" in captured[0].last_questions["type"].criteria
    assert suggestion is not None
    assert suggestion.type == "wip"
