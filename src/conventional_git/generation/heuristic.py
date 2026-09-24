from __future__ import annotations

import re
from typing import TYPE_CHECKING

from conventional_git.generation.protocol import CommitSuggestion
from conventional_git.generation.protocol import register_provider

if TYPE_CHECKING:
    from typing import Final

_TEST_SUFFIXES: Final[tuple[str, ...]] = ("_test.py",)
_TEST_PREFIXES: Final[tuple[str, ...]] = ("tests/", "test/", "tests\\", "test\\")
_DOCS_SUFFIXES: Final[tuple[str, ...]] = (".md", ".rst", ".txt")
_BUILD_FILES: Final[frozenset[str]] = frozenset((
    "pyproject.toml",
    "uv.lock",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
    "Cargo.toml",
    "Cargo.lock",
    "go.mod",
    "go.sum",
    "Makefile",
))
_CI_FILES: Final[frozenset[str]] = frozenset((
    ".gitlab-ci.yml",
    ".pre-commit-config.yaml",
))

_TRAILING_PUNCT: Final[re.Pattern[str]] = re.compile(r"[\s.,;:!?]+$")


class HeuristicProvider:
    name = "heuristic"

    def suggest(
        self,
        diff: str,
        *,
        changed_paths: tuple[str, ...] = (),
    ) -> CommitSuggestion | None:
        if not changed_paths and not diff:
            return None
        paths = changed_paths or _paths_from_diff(diff)
        if not paths:
            return None
        commit_type = infer_type(paths)
        description = infer_description(paths, commit_type)
        return CommitSuggestion(
            type=commit_type,
            scope="",
            description=description,
            confidence=0.5,
        )


def infer_type(paths: tuple[str, ...]) -> str:
    if all(_is_test(p) for p in paths):
        return "test"
    if all(_is_docs(p) for p in paths):
        return "docs"
    if all(_is_build(p) for p in paths):
        return "build"
    if all(_is_ci(p) for p in paths):
        return "ci"
    return "chore"


def _is_test(path: str) -> bool:
    leaf = path.rsplit("/", 1)[-1]
    if any(path.startswith(prefix) for prefix in _TEST_PREFIXES):
        return True
    return leaf.endswith(_TEST_SUFFIXES) or leaf.startswith("test_")


def _is_docs(path: str) -> bool:
    return path.endswith(_DOCS_SUFFIXES)


def _is_build(path: str) -> bool:
    leaf = path.rsplit("/", 1)[-1]
    return leaf in _BUILD_FILES


def _is_ci(path: str) -> bool:
    if path.startswith((".github/", ".circleci/")):
        return True
    leaf = path.rsplit("/", 1)[-1]
    return leaf in _CI_FILES


def infer_description(paths: tuple[str, ...], commit_type: str) -> str:
    first = paths[0].rstrip("/")
    leaf = first.rsplit("/", 1)[-1] if "/" in first else first
    if commit_type == "docs":
        description = f"update {leaf}" if leaf else "update documentation"
    elif commit_type == "test":
        description = "add coverage"
    elif commit_type == "build":
        description = "update dependencies"
    elif commit_type == "ci":
        description = "update pipelines"
    else:
        description = f"update {leaf}" if leaf else "apply changes"
    cleaned = _TRAILING_PUNCT.sub("", description)
    return cleaned[:1].lower() + cleaned[1:]


def _paths_from_diff(diff: str) -> tuple[str, ...]:
    paths: set[str] = set()
    for line in diff.splitlines():
        if line.startswith(("+++ b/", "--- a/")):
            path = line[6:]
            if path != "/dev/null":
                paths.add(path)
    return tuple(sorted(paths))


register_provider(HeuristicProvider())
