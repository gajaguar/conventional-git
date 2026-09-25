from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable


@dataclass(frozen=True, slots=True)
class Config:
    extra_attribution_patterns: tuple[str, ...]
    commit_type_overrides: tuple[Path, ...]
    branch_type_overrides: tuple[Path, ...]
    branch_trunk_overrides: tuple[Path, ...]

    @classmethod
    def load(cls, path: Path | None = None) -> Config:
        if path is None:
            path = Path.cwd() / ".conventional-git.toml"
        if not path.exists():
            return cls(
                extra_attribution_patterns=(),
                commit_type_overrides=(),
                branch_type_overrides=(),
                branch_trunk_overrides=(),
            )
        with path.open("rb") as handle:
            data = tomllib.load(handle)
        commit = data.get("commit", {}) or {}
        branch = data.get("branch", {}) or {}
        # Relative override paths are resolved against the config file's own
        # directory, not the process cwd, so every consumer (CLI, MCP, the
        # gitlint adapter) that loads the same file gets the same paths.
        base = path.parent
        return cls(
            extra_attribution_patterns=tuple(commit.get("attribution_patterns", ()) or ()),
            commit_type_overrides=_resolve_paths(base, commit.get("type_overrides", ()) or ()),
            branch_type_overrides=_resolve_paths(base, branch.get("type_overrides", ()) or ()),
            branch_trunk_overrides=_resolve_paths(base, branch.get("trunk_overrides", ()) or ()),
        )


def _resolve_paths(base: Path, raw: Iterable[str]) -> tuple[Path, ...]:
    resolved: list[Path] = []
    for entry in raw:
        candidate = Path(entry)
        resolved.append(candidate if candidate.is_absolute() else base / candidate)
    return tuple(resolved)
