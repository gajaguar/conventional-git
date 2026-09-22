from __future__ import annotations

import json
import tomllib
from pathlib import Path
from typing import Any

from conventional_git.commit import vocabulary


def schema_pattern() -> str:
    types = vocabulary.default_types()
    return r"(?i)" + "|".join(sorted(types)) + r"(?:\(.+\))?(!)?: .+"


def _schemes() -> dict[str, Any]:
    return {
        "cz_customize": {
            "schema_pattern": schema_pattern(),
            "commit_parser": "",
            "changelog_pattern": "",
        }
    }


def _commitizen_block() -> dict[str, Any]:
    return {
        "name": "cz_customize",
        "tag_format": "$version",
        "version_scheme": "semver",
        "version_provider": "commitizen",
        "update_changelog_on_bump": True,
        "schemes": _schemes(),
    }


def commitizen_config(path: Path | None = None) -> dict[str, Any]:
    if path is None:
        path = Path.cwd() / ".cz.toml"
    if path.exists():
        with path.open("rb") as handle:
            loaded = tomllib.load(handle)
        loaded.setdefault("tool", {})["commitizen"] = _commitizen_block()
        return loaded
    return {"tool": {"commitizen": _commitizen_block()}}


def emit_json(path: Path | None = None) -> str:
    return json.dumps(commitizen_config(path), indent=2)
