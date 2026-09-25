from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from typing import Final

_REPO_ROOT: Final = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("kind", ["commit", "branch"])
def test_skill_vocabulary_matches_core_data(kind: str) -> None:
    # Arrange
    core_csv = _REPO_ROOT / "src" / "conventional_git" / "data" / f"{kind}-types.csv"
    skill_csv = _REPO_ROOT / "skills" / f"conventional-{kind}" / "references" / f"{kind}-types.csv"
    # Act
    core_bytes = core_csv.read_bytes()
    skill_bytes = skill_csv.read_bytes()
    # Assert
    assert skill_bytes == core_bytes, (
        f"{skill_csv} has drifted from {core_csv}; copy the core file into the skill's references/"
    )
