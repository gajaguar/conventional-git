from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Final

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
    types: set[str] = set()
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            branch_type = (row.get("type") or "").strip()
            if branch_type:
                types.add(branch_type)
    return frozenset(types)


def load_trunks_from_csv(path: Path) -> frozenset[str]:
    trunks: set[str] = set()
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            trunk = (row.get("name") or "").strip()
            if trunk:
                trunks.add(trunk)
    return frozenset(trunks)


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
