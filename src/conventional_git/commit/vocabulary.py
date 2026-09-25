from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

from conventional_git.csv_columns import read_column
from conventional_git.csv_columns import read_mapping

if TYPE_CHECKING:
    from typing import Final

    from conventional_git.config import Config

PACKAGE_ROOT: Final[Path] = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=1)
def _load_default() -> frozenset[str]:
    default_path = PACKAGE_ROOT / "data" / "commit-types.csv"
    return frozenset(load_from_csv(default_path))


@lru_cache(maxsize=1)
def _load_default_attribution_patterns() -> tuple[str, ...]:
    default_path = PACKAGE_ROOT / "data" / "commit-attribution.csv"
    return load_attribution_csv(default_path)


@lru_cache(maxsize=1)
def _load_default_criteria() -> dict[str, str]:
    default_path = PACKAGE_ROOT / "data" / "commit-types.csv"
    return load_criteria_from_csv(default_path)


def load_from_csv(path: Path) -> frozenset[str]:
    return frozenset(read_column(path, "type"))


def load_criteria_from_csv(path: Path) -> dict[str, str]:
    return read_mapping(path, "type", "when_to_use")


def load_attribution_csv(path: Path) -> tuple[str, ...]:
    return read_column(path, "pattern")


def default_types() -> frozenset[str]:
    return _load_default()


def default_attribution_patterns() -> tuple[str, ...]:
    return _load_default_attribution_patterns()


def default_criteria() -> dict[str, str]:
    return dict(_load_default_criteria())


def merge_vocabularies(overrides: tuple[Path, ...]) -> frozenset[str]:
    types: set[str] = set(default_types())
    for path in overrides:
        if not path.exists():
            continue
        types |= load_from_csv(path)
    return frozenset(types)


def merge_criteria(overrides: tuple[Path, ...]) -> dict[str, str]:
    criteria: dict[str, str] = dict(_load_default_criteria())
    for path in overrides:
        if not path.exists():
            continue
        criteria |= load_criteria_from_csv(path)
    return criteria


@dataclass(frozen=True, slots=True)
class CommitPolicy:
    types: frozenset[str]
    extra_attribution_patterns: tuple[str, ...]


def resolve_policy(config: Config, *, extra_types_csv: Path | None = None) -> CommitPolicy:
    overrides = (
        (extra_types_csv, *config.commit_type_overrides)
        if extra_types_csv is not None
        else config.commit_type_overrides
    )
    return CommitPolicy(
        types=merge_vocabularies(overrides),
        extra_attribution_patterns=config.extra_attribution_patterns,
    )
