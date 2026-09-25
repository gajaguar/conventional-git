from __future__ import annotations

import json
import tomllib
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Final

_REPO_ROOT: Final = Path(__file__).resolve().parents[1]


def _pyproject_version() -> str:
    data = tomllib.loads((_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return str(data["project"]["version"])


def test_plugin_manifest_version_matches_pyproject() -> None:
    # Arrange
    plugin = json.loads((_REPO_ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    version = _pyproject_version()
    # Act
    # Assert
    assert plugin == {
        "name": "conventional-git",
        "version": version,
        "description": "Conventional Commits and Conventional Branch skills for Claude Code",
        "author": {"name": "G.A.JAGUAR", "email": "dev@gajaguar.com"},
        "license": "MIT",
        "repository": "https://github.com/gajaguar/conventional-git",
        "keywords": [
            "conventional-commits",
            "conventional-branch",
            "commit-message",
            "branch-name",
            "git",
            "skill",
        ],
    }, ".claude-plugin/plugin.json has drifted from pyproject.toml; bump both together on release"


def test_mcp_json_pins_the_same_release_tag_as_pyproject() -> None:
    # Arrange
    manifest = json.loads((_REPO_ROOT / ".mcp.json").read_text(encoding="utf-8"))
    version = _pyproject_version()
    # Act
    # Assert
    assert manifest == {
        "mcpServers": {
            "conventional-git": {
                "command": "uvx",
                "args": [
                    "--from",
                    f"conventional-git[mcp] @ git+https://github.com/gajaguar/conventional-git@v{version}",
                    "conventional-git-mcp",
                ],
            },
        },
    }, f".mcp.json isn't pinned to v{version}; bump the tag alongside pyproject.toml"
