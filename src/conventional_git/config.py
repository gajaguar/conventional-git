from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path


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
        return cls(
            extra_attribution_patterns=tuple(commit.get("attribution_patterns", ()) or ()),
            commit_type_overrides=tuple(Path(p) for p in (commit.get("type_overrides", ()) or ())),
            branch_type_overrides=tuple(Path(p) for p in (branch.get("type_overrides", ()) or ())),
            branch_trunk_overrides=tuple(Path(p) for p in (branch.get("trunk_overrides", ()) or ())),
        )
