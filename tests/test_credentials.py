from __future__ import annotations

from typing import TYPE_CHECKING

from conventional_git.generation import credentials

if TYPE_CHECKING:
    import pytest


def test_resolve_openrouter_key_prefers_the_environment_variable(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    monkeypatch.setenv("OPENROUTER_API_KEY", "env-key")
    monkeypatch.setattr(credentials.keyring, "get_password", lambda *_args: "keyring-key")
    # Act
    resolved = credentials.resolve_openrouter_key()
    # Assert
    assert resolved == "env-key"


def test_resolve_openrouter_key_falls_back_to_the_keyring(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setattr(credentials.keyring, "get_password", lambda *_args: "keyring-key")
    # Act
    resolved = credentials.resolve_openrouter_key()
    # Assert
    assert resolved == "keyring-key"


def test_resolve_openrouter_key_returns_none_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setattr(credentials.keyring, "get_password", lambda *_args: None)
    # Act
    resolved = credentials.resolve_openrouter_key()
    # Assert
    assert resolved is None


def test_resolve_typesafe_key_reads_the_environment_variable(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    monkeypatch.setenv("TYPESAFE_API_KEY", "  native-key  ")
    # Act
    resolved = credentials.resolve_typesafe_key()
    # Assert
    assert resolved == "native-key"


def test_store_openrouter_key_writes_through_the_keyring(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    calls: list[tuple[str, str, str]] = []
    monkeypatch.setattr(credentials.keyring, "set_password", lambda *args: calls.append(args))
    # Act
    credentials.store_openrouter_key("a-key")
    # Assert
    assert calls == [("conventional-git", "openrouter", "a-key")]
