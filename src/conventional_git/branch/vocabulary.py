from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

from conventional_git.csv_columns import read_column

if TYPE_CHECKING:
    from typing import Final

    from conventional_git.config import Config

PACKAGE_ROOT: Final[Path] = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=1)
def _load_default() -> frozenset[str]:
    default_path = PACKAGE_ROOT / "data" / "branch-types.csv"
    return frozenset(load_from_csv(default_path))


@lru_cache(maxsize=1)
def _load_default_trunks() -> frozenset[str]:
    default_path = PACKAGE_ROOT / "data" / "branch-trunks.csv"
    return frozenset(load_trunks_from_csv(default_path))


def load_from_csv(path: Path) -> frozenset[str]:
    return frozenset(read_column(path, "type"))


def load_trunks_from_csv(path: Path) -> frozenset[str]:
    return frozenset(read_column(path, "name"))


def default_types() -> frozenset[str]:
    return _load_default()


def default_trunks() -> frozenset[str]:
    return _load_default_trunks()


def merge_vocabularies(overrides: tuple[Path, ...]) -> frozenset[str]:
    types: set[str] = set(default_types())
    for path in overrides:
        if not path.exists():
            continue
        types |= load_from_csv(path)
    return frozenset(types)


def merge_trunks(overrides: tuple[Path, ...]) -> frozenset[str]:
    trunks: set[str] = set(default_trunks())
    for path in overrides:
        if not path.exists():
            continue
        trunks |= load_trunks_from_csv(path)
    return frozenset(trunks)


@dataclass(frozen=True, slots=True)
class BranchPolicy:
    types: frozenset[str]
    trunks: frozenset[str]


def resolve_policy(
    config: Config,
    *,
    extra_types_csv: Path | None = None,
    extra_trunks_csv: Path | None = None,
) -> BranchPolicy:
    type_overrides = (
        (extra_types_csv, *config.branch_type_overrides)
        if extra_types_csv is not None
        else config.branch_type_overrides
    )
    trunk_overrides = (
        (extra_trunks_csv, *config.branch_trunk_overrides)
        if extra_trunks_csv is not None
        else config.branch_trunk_overrides
    )
    return BranchPolicy(
        types=merge_vocabularies(type_overrides),
        trunks=merge_trunks(trunk_overrides),
    )
