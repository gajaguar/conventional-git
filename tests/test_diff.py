from __future__ import annotations

from typing import TYPE_CHECKING

from conventional_git.generation.diff import FileChange
from conventional_git.generation.diff import change_verb
from conventional_git.generation.diff import parse_diff
from conventional_git.generation.diff import paths_from_diff

if TYPE_CHECKING:
    from typing import Final

_NEW_FILE_DIFF: Final[str] = (
    "diff --git a/docs/usage.md b/docs/usage.md\n"
    "new file mode 100644\n"
    "index 0000000..1234567\n"
    "--- /dev/null\n"
    "+++ b/docs/usage.md\n"
    "@@ -0,0 +1,3 @@\n"
    "+# Usage\n"
    "+\n"
    "+See below.\n"
)

_DELETED_FILE_DIFF: Final[str] = (
    "diff --git a/docs/old.md b/docs/old.md\n"
    "deleted file mode 100644\n"
    "index 1234567..0000000\n"
    "--- a/docs/old.md\n"
    "+++ /dev/null\n"
    "@@ -1,2 +0,0 @@\n"
    "-# Old\n"
    "-content\n"
)

_MODIFIED_FILE_DIFF: Final[str] = (
    "diff --git a/src/foo.py b/src/foo.py\n"
    "index 1234567..89abcde 100644\n"
    "--- a/src/foo.py\n"
    "+++ b/src/foo.py\n"
    "@@ -1,2 +1,2 @@\n"
    "-old\n"
    "+new\n"
    " unchanged\n"
)


def test_parse_diff_classifies_a_new_file() -> None:
    # Arrange
    # Act
    changes = parse_diff(_NEW_FILE_DIFF)
    # Assert
    assert changes == (FileChange(path="docs/usage.md", status="added", added=3, removed=0),)


def test_parse_diff_classifies_a_deleted_file() -> None:
    # Arrange
    # Act
    changes = parse_diff(_DELETED_FILE_DIFF)
    # Assert
    assert changes == (FileChange(path="docs/old.md", status="deleted", added=0, removed=2),)


def test_parse_diff_classifies_a_modified_file() -> None:
    # Arrange
    # Act
    changes = parse_diff(_MODIFIED_FILE_DIFF)
    # Assert
    assert changes == (FileChange(path="src/foo.py", status="modified", added=1, removed=1),)


def test_parse_diff_handles_multiple_files() -> None:
    # Arrange
    diff = _NEW_FILE_DIFF + _MODIFIED_FILE_DIFF
    # Act
    changes = parse_diff(diff)
    # Assert
    assert {change.path for change in changes} == {"docs/usage.md", "src/foo.py"}


def test_paths_from_diff_ignores_file_headers_in_hunk_counts() -> None:
    # Arrange
    # Act
    paths = paths_from_diff(_NEW_FILE_DIFF)
    # Assert
    assert paths == ("docs/usage.md",)


def test_change_verb_is_add_for_a_new_file() -> None:
    # Arrange
    changes = parse_diff(_NEW_FILE_DIFF)
    # Act
    verb = change_verb(changes)
    # Assert
    assert verb == "add"


def test_change_verb_is_remove_for_a_deleted_file() -> None:
    # Arrange
    changes = parse_diff(_DELETED_FILE_DIFF)
    # Act
    verb = change_verb(changes)
    # Assert
    assert verb == "remove"


def test_change_verb_is_update_for_a_modified_file() -> None:
    # Arrange
    changes = parse_diff(_MODIFIED_FILE_DIFF)
    # Act
    verb = change_verb(changes)
    # Assert
    assert verb == "update"


def test_change_verb_is_update_for_no_changes() -> None:
    # Arrange
    # Act
    verb = change_verb(())
    # Assert
    assert verb == "update"
