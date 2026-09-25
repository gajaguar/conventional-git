from __future__ import annotations

import csv
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def read_column(path: Path, column: str) -> tuple[str, ...]:
    values: list[str] = []
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            value = (row.get(column) or "").strip()
            if value:
                values.append(value)
    return tuple(values)


def read_mapping(path: Path, key_column: str, value_column: str) -> dict[str, str]:
    mapping: dict[str, str] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            key = (row.get(key_column) or "").strip()
            value = (row.get(value_column) or "").strip()
            if key:
                mapping[key] = value
    return mapping
