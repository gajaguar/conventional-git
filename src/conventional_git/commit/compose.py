from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import Final

_DEFAULT_DESCRIPTION: Final[str] = "update implementation"
_BULLET_PREFIXES: Final[tuple[str, ...]] = ("- ", "* ")


def normalize_description(description: str | None) -> str:
    normalized = (description or _DEFAULT_DESCRIPTION).strip().rstrip(".").strip() or _DEFAULT_DESCRIPTION
    return normalized[:1].lower() + normalized[1:]


def _as_bullet(line: str) -> str:
    if line.startswith(_BULLET_PREFIXES):
        return line
    return f"- {line.lstrip('-').strip()}"


def build_message(
    commit_type: str,
    scope: str | None,
    description: str,
    body_lines: Iterable[str],
    *,
    breaking: bool,
) -> str:
    scope_segment = f"({scope})" if scope else ""
    exclamation = "!" if breaking else ""
    normalized_description = normalize_description(description)
    title = f"{commit_type}{scope_segment}{exclamation}: {normalized_description}"
    body_text = "\n".join(_as_bullet(line) for line in body_lines)
    if breaking:
        return f"{title}\n\n{body_text}\n\nBREAKING CHANGE: {normalized_description}"
    return f"{title}\n\n{body_text}" if body_text else title
