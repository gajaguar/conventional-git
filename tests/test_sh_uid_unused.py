from __future__ import annotations

import importlib.util
import re
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Final

_REPO_ROOT: Final = Path(__file__).resolve().parents[1]
_SH_UID_OPTION: Final = re.compile(r"\b_uid\b")


def _files_using_sh_uid(root: Path) -> list[str]:
    return sorted(
        str(path.relative_to(root))
        for path in root.rglob("*.py")
        if _SH_UID_OPTION.search(path.read_text(encoding="utf-8"))
    )


def test_gitlint_does_not_pass_the_sh_uid_option() -> None:
    # Arrange
    spec = importlib.util.find_spec("gitlint")
    assert spec is not None
    assert spec.origin is not None
    # Act
    offenders = _files_using_sh_uid(Path(spec.origin).parent)
    # Assert
    assert offenders == [], "gitlint now uses sh's _uid option; revisit docs/toolchain/sh-uid-unused.md"


def test_own_source_does_not_pass_the_sh_uid_option() -> None:
    # Arrange
    # Act
    offenders = _files_using_sh_uid(_REPO_ROOT / "src")
    # Assert
    assert offenders == [], "src now uses sh's _uid option; revisit docs/toolchain/sh-uid-unused.md"
