from __future__ import annotations

import json
from importlib.metadata import version as package_version
from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from conventional_git.cli import capabilities as capabilities_module
from conventional_git.generation import credentials

if TYPE_CHECKING:
    from typing import Final

_RUNNER: Final = CliRunner()
_EXPECTED_MCP_TOOLS: Final = (
    "validate_commit_message",
    "validate_branch_name",
    "describe_convention",
    "suggest_commit_message",
)


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


def _invoke_json() -> dict[str, object]:
    result = _RUNNER.invoke(capabilities_module.app, ["--json"])
    payload: dict[str, object] = json.loads(result.stdout)
    assert result.exit_code == 0
    return payload


@pytest.mark.usefixtures("fake_keyring")
def test_json_reports_the_full_capabilities_shape_with_no_credentials_set() -> None:
    # Arrange
    # Act
    payload = _invoke_json()
    # Assert
    assert payload == {
        "version": package_version("conventional-git"),
        "extras": {"llm": True, "mcp": True, "gitlint": True},
        "providers": ["heuristic", "jev"],
        "credentials": {"typesafe": None, "openrouter": None},
        "mcp_tools": list(_EXPECTED_MCP_TOOLS),
    }


@pytest.mark.usefixtures("fake_keyring")
def test_json_reports_the_keyring_source_without_leaking_the_key() -> None:
    # Arrange
    credentials.store_key("openrouter", "a-secret-key")
    # Act
    result = _RUNNER.invoke(capabilities_module.app, ["--json"])
    payload = json.loads(result.stdout)
    # Assert
    assert payload == {
        "version": package_version("conventional-git"),
        "extras": {"llm": True, "mcp": True, "gitlint": True},
        "providers": ["heuristic", "jev"],
        "credentials": {"typesafe": None, "openrouter": "keyring"},
        "mcp_tools": list(_EXPECTED_MCP_TOOLS),
    }
    assert "a-secret-key" not in result.stdout


@pytest.mark.usefixtures("fake_keyring")
def test_json_reports_the_environment_source(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    monkeypatch.setenv("OPENROUTER_API_KEY", "env-key")
    # Act
    result = _RUNNER.invoke(capabilities_module.app, ["--json"])
    payload = json.loads(result.stdout)
    # Assert
    assert payload == {
        "version": package_version("conventional-git"),
        "extras": {"llm": True, "mcp": True, "gitlint": True},
        "providers": ["heuristic", "jev"],
        "credentials": {"typesafe": None, "openrouter": "env"},
        "mcp_tools": list(_EXPECTED_MCP_TOOLS),
    }
    assert "env-key" not in result.stdout


@pytest.mark.usefixtures("fake_keyring")
def test_human_readable_output_lists_every_credential_by_provider() -> None:
    # Arrange
    # Act
    result = _RUNNER.invoke(capabilities_module.app, [])
    # Assert
    assert result.exit_code == 0
    assert "credential[typesafe]: not set" in result.stdout
    assert "credential[openrouter]: not set" in result.stdout
