from __future__ import annotations

import re
import unicodedata
from typing import Final

from conventional_git.branch import grammar
from conventional_git.branch import vocabulary
from conventional_git.violations import Report
from conventional_git.violations import Severity
from conventional_git.violations import Violation

DEFAULT_DESCRIPTION: Final[str] = "work-in-progress"


def _violation(
    code: str,
    field: str,
    message: str,
    fix_hint: str,
    *,
    severity: Severity = Severity.ERROR,
) -> Violation:
    return Violation(code=code, field=field, message=message, fix_hint=fix_hint, severity=severity)


def normalize_description(raw: str | None) -> str:
    text = unicodedata.normalize("NFKD", raw or DEFAULT_DESCRIPTION)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.replace("_", "-").replace(" ", "-").lower()
    text = re.sub(r"[^a-z0-9.\-]", "", text)
    text = re.sub(r"\.{2,}", ".", text)
    text = re.sub(r"-{2,}", "-", text)
    text = re.sub(r"[.\-]?-[.\-]?", "-", text)
    text = text.strip("-.")
    if len(text) > grammar.description_max_length():
        text = text[: grammar.description_max_length()].rsplit("-", 1)[0].strip("-.")
    if not text:
        text = DEFAULT_DESCRIPTION
    return text


def build_branch_name(branch_type: str, description: str) -> str:
    return f"{branch_type}/{description}"


def validate_name(
    name: str,
    *,
    allowed_types: frozenset[str] | None = None,
    trunk_branches: frozenset[str] | None = None,
) -> Report:
    trunks = trunk_branches if trunk_branches is not None else vocabulary.default_trunks()
    if name in trunks:
        return Report.from_violations()

    types = allowed_types if allowed_types is not None else vocabulary.default_types()
    parsed = grammar.parse(name)
    if parsed is None:
        return Report.from_violations(
            _violation(
                "branch.format",
                "name",
                f"Branch name {name!r} does not match <type>/<description>",
                "Use the form 'type/description' (lowercase letters, digits, hyphens, dots)",
            )
        )

    violations: list[Violation] = []
    branch_type = parsed["type"]
    description = parsed["description"]

    if branch_type not in types:
        violations.append(
            _violation(
                "branch.type",
                "type",
                f"Branch type {branch_type!r} is not allowed",
                f"Use one of: {', '.join(sorted(types))}",
            )
        )
    if not description:
        violations.append(
            _violation(
                "branch.description-empty",
                "description",
                "Description segment is empty",
                "Provide a non-empty hyphenated description",
            )
        )
    if len(description) > grammar.description_max_length():
        violations.append(
            _violation(
                "branch.description-length",
                "description",
                f"Description exceeds {grammar.description_max_length()} characters ({len(description)})",
                f"Shorten the description to at most {grammar.description_max_length()} characters",
            )
        )

    return Report.from_violations(*violations)


def default_description() -> str:
    return DEFAULT_DESCRIPTION
