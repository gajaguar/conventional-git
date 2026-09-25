from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Final

MAX_TITLE_LENGTH: Final[int] = 120

_DESCRIPTION_PATTERN: Final[re.Pattern[str]] = re.compile(r"^[a-z0-9].*$")
_SCOPE: Final[str] = r"[a-z0-9.\-]+"
_SCOPE_PATTERN: Final[re.Pattern[str]] = re.compile(rf"^{_SCOPE}$")
# §16 allows BREAKING-CHANGE; line anchoring and spaces keep its nonblank value on that line.
_BREAKING_FOOTER_PATTERN: Final[re.Pattern[str]] = re.compile(r"^BREAKING[ -]CHANGE: *\S.*$", re.MULTILINE)
_TITLE_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^(?P<type>[a-z]+)"
    rf"(?:\((?P<scope>{_SCOPE})\))?"
    r"(?P<breaking>!)?"
    r": (?P<description>.+)$"
)
TRAILING_DOT: Final[re.Pattern[str]] = re.compile(r"\.\s*$")


def split_title(title: str) -> dict[str, str] | None:
    match = _TITLE_PATTERN.match(title)
    if not match:
        return None
    return match.groupdict()


def is_valid_description(text: str) -> bool:
    return bool(_DESCRIPTION_PATTERN.match(text))


def is_valid_scope(text: str) -> bool:
    return bool(_SCOPE_PATTERN.fullmatch(text))


def has_breaking_footer(message: str) -> bool:
    return bool(_BREAKING_FOOTER_PATTERN.search(message))
