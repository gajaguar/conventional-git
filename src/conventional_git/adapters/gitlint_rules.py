from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any

from gitlint.options import BoolOption
from gitlint.rules import CommitRule
from gitlint.rules import RuleViolation

from conventional_git.commit import rules as commit_rules
from conventional_git.commit import vocabulary as commit_vocab
from conventional_git.config import Config
from conventional_git.violations import Severity

if TYPE_CHECKING:
    from typing import ClassVar
    from typing import Final

    from gitlint.git import GitCommit
    from gitlint.options import RuleOption

# gitlint built-ins that duplicate or contradict the core checks; `.gitlint`
# should carry `ignore=<these>` so the adapter holds the only verdict.
RECOMMENDED_IGNORE: Final[tuple[str, ...]] = ("B1", "B5", "B6", "T1", "T3", "T5")


def _repo_root(commit: GitCommit) -> Path:
    repository_path = commit.context.repository_path
    return Path(repository_path) if repository_path else Path.cwd()


def _config(commit: GitCommit) -> tuple[frozenset[str], tuple[str, ...]]:
    root = _repo_root(commit)
    config = Config.load(root / ".conventional-git.toml")
    overrides = tuple(path if path.is_absolute() else root / path for path in config.commit_type_overrides)
    allowed_types = commit_vocab.merge_vocabularies(overrides)
    return allowed_types, config.extra_attribution_patterns


def _to_gitlint(
    message: str,
    *,
    allowed_types: frozenset[str] | None = None,
    attribution_patterns: tuple[str, ...] = (),
    include_warnings: bool = False,
) -> list[RuleViolation]:
    report = commit_rules.validate_message(
        message,
        allowed_types=allowed_types,
        attribution_patterns=attribution_patterns,
    )
    violations: list[RuleViolation] = []
    for violation in report.violations:
        is_warning = violation.severity is Severity.WARNING
        if is_warning and not include_warnings:
            continue
        label = "WARNING" if is_warning else "ERROR"
        violations.append(
            RuleViolation(
                rule_id=f"conventional-git/{violation.code}",
                message=f"{label}: {violation.field}: {violation.message}",
                content=violation.fix_hint,
            )
        )
    return violations


class ConventionalCommitHeaderRule(CommitRule):  # type: ignore[misc]
    name = "conventional-git-header"
    id = "CG1"
    options_spec: ClassVar[list[RuleOption]] = [
        BoolOption(name="warnings", value=False, description="Report core warnings as gitlint violations")
    ]

    def validate(self, commit: GitCommit) -> list[RuleViolation]:
        allowed_types, attribution_patterns = _config(commit)
        return _to_gitlint(
            commit.message.original,
            allowed_types=allowed_types,
            attribution_patterns=attribution_patterns,
            include_warnings=bool(self.options["warnings"].value),
        )


def rule_classes() -> list[type[Any]]:
    return [ConventionalCommitHeaderRule]


__all__ = [
    "RECOMMENDED_IGNORE",
    "ConventionalCommitHeaderRule",
    "rule_classes",
]
