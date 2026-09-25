from __future__ import annotations

import re
from typing import TYPE_CHECKING

from conventional_git.commit import grammar
from conventional_git.commit import vocabulary
from conventional_git.violations import Report
from conventional_git.violations import Severity
from conventional_git.violations import Violation

if TYPE_CHECKING:
    from typing import Final

_BODY_LINE_MAX: Final[int] = 140
_MESSAGE_MAX_BYTES: Final[int] = 2048
_BULLET_PREFIXES: Final[tuple[str, ...]] = ("- ", "* ")


def _violation(
    code: str,
    field: str,
    message: str,
    fix_hint: str,
    *,
    severity: Severity = Severity.ERROR,
) -> Violation:
    return Violation(code=code, field=field, message=message, fix_hint=fix_hint, severity=severity)


def _parse_header(message: str) -> tuple[str, str | None, bool, str] | None:
    header = message.split("\n", 1)[0].strip()
    parsed = grammar.split_title(header)
    if parsed is None:
        return None
    return (
        parsed["type"],
        parsed.get("scope"),
        bool(parsed.get("breaking")),
        parsed["description"],
    )


_BODY_SPLIT_PARTS: Final[int] = 2


def _body_lines(message: str) -> list[str]:
    parts = message.split("\n", 1)
    if len(parts) < _BODY_SPLIT_PARTS:
        return []
    body = parts[1].split("\n\n", 1)[0]
    return [line for line in body.splitlines() if line.strip()]


def _is_bullet(line: str) -> bool:
    return line.lstrip().startswith(_BULLET_PREFIXES)


def _check_header(parsed: tuple[str, str | None, bool, str] | None, types: frozenset[str]) -> list[Violation]:
    if parsed is None:
        return [
            _violation(
                "commit.header-format",
                "header",
                "Header does not match <type>[(<scope>)][!]: <description>",
                "Use the form 'type(scope)!: description' (scope and ! optional)",
            )
        ]
    commit_type, _scope, _breaking_marker, description = parsed
    violations: list[Violation] = []
    if commit_type not in types:
        violations.append(
            _violation(
                "commit.type",
                "type",
                f"Commit type {commit_type!r} is not allowed",
                f"Use one of: {', '.join(sorted(types))}",
            )
        )
    if not grammar.is_valid_description(description):
        violations.append(
            _violation(
                "commit.description-format",
                "description",
                "Description must start with a lowercase letter or digit and use only lowercase characters",
                "Rewrite the description in lowercase, imperative, present tense",
            )
        )
    if grammar.TRAILING_DOT.search(description):
        violations.append(
            _violation(
                "commit.description-trailing-period",
                "description",
                "Description must not end with a period",
                "Remove the trailing period",
                severity=Severity.WARNING,
            )
        )
    return violations


def _check_title_length(message: str) -> list[Violation]:
    title = message.split("\n", 1)[0]
    if grammar.title_length(title) > grammar.title_max_length():
        return [
            _violation(
                "commit.title-length",
                "title",
                f"Title exceeds {grammar.title_max_length()} characters",
                f"Shorten the title to at most {grammar.title_max_length()} characters",
            )
        ]
    return []


def _check_body_lines(message: str) -> list[Violation]:
    violations: list[Violation] = []
    for index, line in enumerate(_body_lines(message)):
        if len(line) > _BODY_LINE_MAX:
            violations.append(
                _violation(
                    "commit.body-line-length",
                    f"body[{index}]",
                    f"Body line {index + 1} exceeds {_BODY_LINE_MAX} characters ({len(line)})",
                    f"Wrap or shorten the line to at most {_BODY_LINE_MAX} characters",
                )
            )
        if not _is_bullet(line):
            violations.append(
                _violation(
                    "commit.body-bullet",
                    f"body[{index}]",
                    f"Body line {index + 1} is not a bullet",
                    "Prefix the line with '- ' or '* '",
                    severity=Severity.WARNING,
                )
            )
    return violations


def _check_message_bytes(message: str) -> list[Violation]:
    byte_length = len(message.encode("utf-8"))
    if byte_length > _MESSAGE_MAX_BYTES:
        return [
            _violation(
                "commit.message-bytes",
                "message",
                f"Message exceeds {_MESSAGE_MAX_BYTES} bytes ({byte_length})",
                "Shorten the message so its UTF-8 encoding fits within the byte limit",
            )
        ]
    return []


def _check_breaking_footer(parsed: tuple[str, str | None, bool, str] | None, message: str) -> list[Violation]:
    if parsed is not None and parsed[2] and not grammar.has_breaking_footer(message):
        return [
            _violation(
                "commit.breaking-footer",
                "footer",
                "Header marks a breaking change but no 'BREAKING CHANGE:' footer was found",
                "Append 'BREAKING CHANGE: <description>' after the body",
            )
        ]
    return []


def _check_attribution(message: str, patterns: tuple[str, ...]) -> list[Violation]:
    if not patterns:
        return []
    combined = re.compile("|".join(patterns), re.IGNORECASE)
    body_lines = message.split("\n", 1)[1].splitlines() if "\n" in message else []
    violations: list[Violation] = []
    for index, line in enumerate(body_lines):
        stripped = line.strip()
        if stripped and combined.search(stripped):
            violations.append(
                _violation(
                    "commit.attribution",
                    f"footer[{index}]",
                    f"Attribution line is not allowed: {stripped}",
                    "Remove the attribution trailer",
                )
            )
    return violations


def validate_message(
    message: str,
    *,
    allowed_types: frozenset[str] | None = None,
    attribution_patterns: tuple[str, ...] | None = None,
) -> Report:
    if not message or not message.strip():
        return Report.from_violations(
            _violation(
                "commit.empty",
                "message",
                "Commit message is empty",
                "Provide a non-empty commit message",
            )
        )

    types = allowed_types if allowed_types is not None else vocabulary.default_types()
    patterns = vocabulary.default_attribution_patterns() + (attribution_patterns or ())
    parsed = _parse_header(message)
    violations: list[Violation] = []
    violations.extend(_check_header(parsed, types))
    violations.extend(_check_title_length(message))
    violations.extend(_check_body_lines(message))
    violations.extend(_check_message_bytes(message))
    violations.extend(_check_breaking_footer(parsed, message))
    violations.extend(_check_attribution(message, patterns))
    return Report.from_violations(*violations)


def message_max_bytes() -> int:
    return _MESSAGE_MAX_BYTES


def body_line_max() -> int:
    return _BODY_LINE_MAX
