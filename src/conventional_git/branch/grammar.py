from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Final

MAX_DESCRIPTION_LENGTH: Final[int] = 75

_SEGMENT: Final[str] = r"[a-z0-9]+(?:\.[a-z0-9]+)*"
_BRANCH_NAME_PATTERN: Final[re.Pattern[str]] = re.compile(
    rf"^(?P<type>[a-z]+)/(?P<description>{_SEGMENT}(?:-{_SEGMENT})*)$"
)


def parse(name: str) -> dict[str, str] | None:
    match = _BRANCH_NAME_PATTERN.match(name)
    if not match:
        return None
    return match.groupdict()
