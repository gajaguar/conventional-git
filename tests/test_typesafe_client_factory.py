from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from conventional_git.generation import typesafe
from conventional_git.generation.protocol import MissingCredentialsError

if TYPE_CHECKING:
    from typing import Final


@pytest.fixture
def _clear_credential_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("TYPESAFE_BASE_URL", raising=False)
    monkeypatch.delenv("TYPESAFE_DEFAULT_MODEL", raising=False)
    monkeypatch.setattr(typesafe.credentials.keyring, "get_password", lambda *_args: None)


def _capture_client_kwargs(monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
    captured: dict[str, object] = {}

    def _fake_client(**kwargs: object) -> object:
        captured.update(kwargs)
        return object()

    monkeypatch.setattr(typesafe, "TypeSafeClient", _fake_client)
    return captured


def _openrouter_only_password(service: str, user: str) -> str | None:
    del service
    return "keyring-key" if user == "openrouter" else None


@pytest.mark.usefixtures("_clear_credential_env")
def test_build_client_uses_a_typesafe_key_directly(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    monkeypatch.setenv("TYPESAFE_API_KEY", "typesafe-key")
    captured = _capture_client_kwargs(monkeypatch)
    # Act
    typesafe._build_client()  # ruff: ignore[private-member-access]  # pylint: disable=protected-access
    # Assert
    assert captured == {"api_key": "typesafe-key"}


@pytest.mark.usefixtures("_clear_credential_env")
def test_build_client_uses_an_openrouter_key_from_the_keyring(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    monkeypatch.setattr(typesafe.credentials.keyring, "get_password", _openrouter_only_password)
    captured = _capture_client_kwargs(monkeypatch)
    # Act
    typesafe._build_client()  # ruff: ignore[private-member-access]  # pylint: disable=protected-access
    # Assert
    assert captured == {
        "api_key": "keyring-key",
        "base_url": "https://openrouter.ai/api",
        "model": "typesafe/jev-1.13",
    }


_MISSING_CREDENTIALS_MATCH: Final[str] = "TYPESAFE_API_KEY"


@pytest.mark.usefixtures("_clear_credential_env")
def test_build_client_raises_missing_credentials_naming_both_env_vars() -> None:
    # Arrange
    # Act
    # Assert
    with pytest.raises(MissingCredentialsError, match=_MISSING_CREDENTIALS_MATCH):
        typesafe._build_client()  # ruff: ignore[private-member-access]  # pylint: disable=protected-access
