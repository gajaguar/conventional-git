from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from conventional_git.generation import credentials
from conventional_git.generation.protocol import MissingCredentialsError

if TYPE_CHECKING:
    from typing import Final

_NO_KEYRING_BACKEND_MESSAGE: Final[str] = "no backend"


class _FakeKeyring:
    def __init__(self) -> None:
        self._store: dict[tuple[str, str], str] = {}

    def get_password(self, service: str, user: str) -> str | None:
        return self._store.get((service, user))

    def set_password(self, service: str, user: str, key: str) -> None:
        self._store[service, user] = key

    def delete_password(self, service: str, user: str) -> None:
        self._store.pop((service, user), None)


@pytest.fixture
def fake_keyring(monkeypatch: pytest.MonkeyPatch) -> _FakeKeyring:
    fake = _FakeKeyring()
    monkeypatch.setattr(credentials.keyring, "get_password", fake.get_password)
    monkeypatch.setattr(credentials.keyring, "set_password", fake.set_password)
    monkeypatch.setattr(credentials.keyring, "delete_password", fake.delete_password)
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    return fake


def _raise_keyring_error(*_args: object) -> None:
    raise credentials.KeyringError(_NO_KEYRING_BACKEND_MESSAGE)


def test_env_key_reads_and_strips_the_environment_variable(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    monkeypatch.setenv("TYPESAFE_API_KEY", "  native-key  ")
    # Act
    resolved = credentials.env_key("typesafe")
    # Assert
    assert resolved == "native-key"


def test_env_key_returns_none_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    # Act
    resolved = credentials.env_key("openrouter")
    # Assert
    assert resolved is None


@pytest.mark.usefixtures("fake_keyring")
def test_stored_key_returns_none_when_nothing_is_stored() -> None:
    # Arrange
    # Act
    resolved = credentials.stored_key("openrouter")
    # Assert
    assert resolved is None


@pytest.mark.usefixtures("fake_keyring")
def test_store_and_stored_key_round_trip() -> None:
    # Arrange
    # Act
    credentials.store_key("openrouter", "a-key")
    # Assert
    assert credentials.stored_key("openrouter") == "a-key"


def test_store_key_writes_under_the_provider_name_as_the_keyring_user(fake_keyring: _FakeKeyring) -> None:
    # Arrange
    # Act
    credentials.store_key("typesafe", "a-typesafe-key")
    # Assert
    assert fake_keyring.get_password("conventional-git", "typesafe") == "a-typesafe-key"


@pytest.mark.usefixtures("fake_keyring")
def test_store_key_rejects_an_unknown_provider() -> None:
    # Arrange
    # Act
    # Assert
    with pytest.raises(ValueError, match="Unknown provider"):
        credentials.store_key("bogus", "a-key")


def test_store_key_raises_missing_credentials_without_a_keyring_backend(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    monkeypatch.setattr(credentials.keyring, "set_password", _raise_keyring_error)
    # Act
    # Assert
    with pytest.raises(MissingCredentialsError, match="TYPESAFE_API_KEY"):
        credentials.store_key("typesafe", "a-key")


@pytest.mark.usefixtures("fake_keyring")
def test_clear_key_removes_the_stored_entry() -> None:
    # Arrange
    credentials.store_key("openrouter", "a-key")
    # Act
    credentials.clear_key("openrouter")
    # Assert
    assert credentials.stored_key("openrouter") is None


@pytest.mark.usefixtures("fake_keyring")
def test_clear_key_rejects_an_unknown_provider() -> None:
    # Arrange
    # Act
    # Assert
    with pytest.raises(ValueError, match="Unknown provider"):
        credentials.clear_key("bogus")


@pytest.mark.usefixtures("fake_keyring")
def test_resolve_credential_prefers_env_over_keyring(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    credentials.store_key("openrouter", "keyring-key")
    monkeypatch.setenv("OPENROUTER_API_KEY", "env-key")
    # Act
    resolved = credentials.resolve_credential("openrouter")
    # Assert
    assert resolved == credentials.Credential(provider="openrouter", key="env-key", source="env")


@pytest.mark.usefixtures("fake_keyring")
def test_resolve_credential_falls_back_to_the_keyring() -> None:
    # Arrange
    credentials.store_key("openrouter", "keyring-key")
    # Act
    resolved = credentials.resolve_credential("openrouter")
    # Assert
    assert resolved == credentials.Credential(provider="openrouter", key="keyring-key", source="keyring")


@pytest.mark.usefixtures("fake_keyring")
def test_resolve_credential_returns_none_when_nothing_is_set() -> None:
    # Arrange
    # Act
    resolved = credentials.resolve_credential("typesafe")
    # Assert
    assert resolved is None


@pytest.mark.usefixtures("fake_keyring")
def test_resolve_active_credential_prefers_typesafe_env_over_openrouter_env(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    monkeypatch.setenv("TYPESAFE_API_KEY", "typesafe-env")
    monkeypatch.setenv("OPENROUTER_API_KEY", "openrouter-env")
    # Act
    resolved = credentials.resolve_active_credential()
    # Assert
    assert resolved == credentials.Credential(provider="typesafe", key="typesafe-env", source="env")


@pytest.mark.usefixtures("fake_keyring")
def test_resolve_active_credential_prefers_openrouter_env_over_typesafe_keyring(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    credentials.store_key("typesafe", "typesafe-keyring")
    monkeypatch.setenv("OPENROUTER_API_KEY", "openrouter-env")
    # Act
    resolved = credentials.resolve_active_credential()
    # Assert
    assert resolved == credentials.Credential(provider="openrouter", key="openrouter-env", source="env")


@pytest.mark.usefixtures("fake_keyring")
def test_resolve_active_credential_prefers_typesafe_keyring_over_openrouter_keyring() -> None:
    # Arrange
    credentials.store_key("typesafe", "typesafe-keyring")
    credentials.store_key("openrouter", "openrouter-keyring")
    # Act
    resolved = credentials.resolve_active_credential()
    # Assert
    assert resolved == credentials.Credential(provider="typesafe", key="typesafe-keyring", source="keyring")


@pytest.mark.usefixtures("fake_keyring")
def test_resolve_active_credential_finds_a_legacy_openrouter_only_entry() -> None:
    # Arrange
    credentials.store_key("openrouter", "legacy-key")
    # Act
    resolved = credentials.resolve_active_credential()
    # Assert
    assert resolved == credentials.Credential(provider="openrouter", key="legacy-key", source="keyring")


@pytest.mark.usefixtures("fake_keyring")
def test_resolve_active_credential_returns_none_when_nothing_is_set() -> None:
    # Arrange
    # Act
    resolved = credentials.resolve_active_credential()
    # Assert
    assert resolved is None
