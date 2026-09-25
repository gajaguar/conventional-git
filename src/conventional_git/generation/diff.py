from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Final

_SECTION_MARKER: Final[str] = "diff --git "


class ChangeStatus(StrEnum):
    ADDED = "added"
    DELETED = "deleted"
    MODIFIED = "modified"


@dataclass(frozen=True, slots=True)
class FileChange:
    path: str
    status: ChangeStatus
    added: int
    removed: int


def parse_diff(diff: str) -> tuple[FileChange, ...]:
    if not diff:
        return ()
    sections = _split_sections(diff)
    changes = [change for section in sections if (change := _parse_section(section)) is not None]
    return tuple(changes)


def paths_from_diff(diff: str) -> tuple[str, ...]:
    return tuple(sorted({change.path for change in parse_diff(diff)}))


def change_verb(changes: tuple[FileChange, ...]) -> str:
    if not changes:
        return "update"
    if all(change.status == ChangeStatus.ADDED for change in changes):
        return "add"
    if all(change.status == ChangeStatus.DELETED for change in changes):
        return "remove"
    added = sum(change.added for change in changes)
    removed = sum(change.removed for change in changes)
    if added and not removed:
        return "add"
    if removed and not added:
        return "remove"
    return "update"


def _split_sections(diff: str) -> list[str]:
    if _SECTION_MARKER not in diff:
        return [diff]
    sections: list[str] = []
    current: list[str] = []
    for line in diff.splitlines(keepends=True):
        if line.startswith(_SECTION_MARKER) and current:
            sections.append("".join(current))
            current = []
        current.append(line)
    if current:
        sections.append("".join(current))
    return sections


@dataclass(slots=True)
class _SectionState:
    status: ChangeStatus = ChangeStatus.MODIFIED
    path: str | None = None
    old_path: str | None = None
    added: int = 0
    removed: int = 0
    in_hunk: bool = False


def _parse_section(section: str) -> FileChange | None:
    state = _SectionState()
    for line in section.splitlines():
        _apply_line(state, line)
    resolved_path = state.path or state.old_path
    if resolved_path is None:
        return None
    return FileChange(path=resolved_path, status=state.status, added=state.added, removed=state.removed)


def _apply_line(state: _SectionState, line: str) -> None:
    if line.startswith("@@"):
        state.in_hunk = True
        return
    if line.startswith("new file mode"):
        state.status = ChangeStatus.ADDED
        return
    if line.startswith("deleted file mode"):
        state.status = ChangeStatus.DELETED
        return
    if line.startswith("--- "):
        state.in_hunk = False
        _apply_old_header(state, line[4:])
        return
    if line.startswith("+++ "):
        state.in_hunk = False
        _apply_new_header(state, line[4:])
        return
    if not state.in_hunk:
        return
    _apply_hunk_line(state, line)


def _apply_old_header(state: _SectionState, target: str) -> None:
    if target == "/dev/null":
        state.status = ChangeStatus.ADDED
    elif target.startswith("a/"):
        state.old_path = target[2:]


def _apply_new_header(state: _SectionState, target: str) -> None:
    if target == "/dev/null":
        state.status = ChangeStatus.DELETED
    elif target.startswith("b/"):
        state.path = target[2:]


def _apply_hunk_line(state: _SectionState, line: str) -> None:
    if line.startswith("+"):
        state.added += 1
    elif line.startswith("-"):
        state.removed += 1
