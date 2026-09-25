from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from conventional_git.cli import auth as auth_module
from conventional_git.generation import credentials

if TYPE_CHECKING:
    from typing import Final

_RUNNER: Final = CliRunner()
_INVALID_PROVIDER_EXIT_CODE: Final[int] = 2


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


@pytest.mark.usefixtures("fake_keyring")
def test_login_stores_an_openrouter_key_by_default() -> None:
    # Arrange
    # Act
    result = _RUNNER.invoke(auth_module.app, ["login"], input="a-key\n")
    # Assert
    assert result.exit_code == 0
    assert "OpenRouter" in result.stdout
    assert credentials.stored_key("openrouter") == "a-key"


@pytest.mark.usefixtures("fake_keyring")
def test_login_stores_a_typesafe_key_with_the_provider_flag() -> None:
    # Arrange
    # Act
    result = _RUNNER.invoke(auth_module.app, ["login", "--provider", "typesafe"], input="a-typesafe-key\n")
    # Assert
    assert result.exit_code == 0
    assert "TypeSafe" in result.stdout
    assert credentials.stored_key("typesafe") == "a-typesafe-key"


@pytest.mark.usefixtures("fake_keyring")
def test_login_rejects_an_unknown_provider() -> None:
    # Arrange
    # Act
    result = _RUNNER.invoke(auth_module.app, ["login", "--provider", "bogus"], input="a-key\n")
    # Assert
    assert result.exit_code == _INVALID_PROVIDER_EXIT_CODE
    assert "Unknown provider" in result.stderr


@pytest.mark.usefixtures("fake_keyring")
def test_login_refuses_an_empty_key() -> None:
    # Arrange
    # Act
    result = _RUNNER.invoke(auth_module.app, ["login"], input="  \n")
    # Assert
    assert result.exit_code == 1
    assert "empty" in result.stderr


@pytest.mark.usefixtures("fake_keyring")
def test_logout_without_a_provider_removes_every_stored_key() -> None:
    # Arrange
    credentials.store_key("openrouter", "a-key")
    credentials.store_key("typesafe", "another-key")
    # Act
    result = _RUNNER.invoke(auth_module.app, ["logout"])
    # Assert
    assert result.exit_code == 0
    assert credentials.stored_key("openrouter") is None
    assert credentials.stored_key("typesafe") is None


@pytest.mark.usefixtures("fake_keyring")
def test_logout_with_a_provider_removes_only_that_key() -> None:
    # Arrange
    credentials.store_key("openrouter", "a-key")
    credentials.store_key("typesafe", "another-key")
    # Act
    result = _RUNNER.invoke(auth_module.app, ["logout", "--provider", "typesafe"])
    # Assert
    assert result.exit_code == 0
    assert credentials.stored_key("openrouter") == "a-key"
    assert credentials.stored_key("typesafe") is None


@pytest.mark.usefixtures("fake_keyring")
def test_logout_rejects_an_unknown_provider() -> None:
    # Arrange
    # Act
    result = _RUNNER.invoke(auth_module.app, ["logout", "--provider", "bogus"])
    # Assert
    assert result.exit_code == _INVALID_PROVIDER_EXIT_CODE


@pytest.mark.usefixtures("fake_keyring")
def test_status_reports_no_credentials_when_unset() -> None:
    # Arrange
    # Act
    result = _RUNNER.invoke(auth_module.app, ["status"])
    # Assert
    assert result.exit_code == 0
    assert "No credentials found" in result.stdout


@pytest.mark.usefixtures("fake_keyring")
def test_status_reports_each_provider_and_marks_the_active_one() -> None:
    # Arrange
    credentials.store_key("openrouter", "openrouter-key")
    credentials.store_key("typesafe", "typesafe-key")
    # Act
    result = _RUNNER.invoke(auth_module.app, ["status"])
    # Assert
    assert result.exit_code == 0
    lines = result.stdout.splitlines()
    typesafe_line = next(line for line in lines if line.startswith("TypeSafe:"))
    openrouter_line = next(line for line in lines if line.startswith("OpenRouter:"))
    assert "keyring" in typesafe_line
    assert "(active)" in typesafe_line
    assert "keyring" in openrouter_line
    assert "(active)" not in openrouter_line


@pytest.mark.usefixtures("fake_keyring")
def test_status_reports_the_environment_source(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    monkeypatch.setenv("OPENROUTER_API_KEY", "env-key")
    # Act
    result = _RUNNER.invoke(auth_module.app, ["status"])
    # Assert
    assert "env (OPENROUTER_API_KEY)" in result.stdout
