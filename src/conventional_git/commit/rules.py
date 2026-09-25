from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import NamedTuple

from conventional_git.commit import grammar
from conventional_git.commit import vocabulary
from conventional_git.violations import Report
from conventional_git.violations import Severity
from conventional_git.violations import Violation
from conventional_git.violations import ViolationCode

if TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Iterable
    from typing import Final

_BODY_LINE_MAX: Final[int] = 140
_MESSAGE_MAX_BYTES: Final[int] = 2048
_BULLET_PREFIXES: Final[tuple[str, ...]] = ("- ", "* ")


class Header(NamedTuple):
    type: str
    scope: str | None
    breaking: bool
    description: str


@dataclass(frozen=True, slots=True)
class ParsedMessage:
    message: str
    header: Header | None


@dataclass(frozen=True, slots=True)
class _RulePolicy:
    types: frozenset[str]
    attribution_patterns: tuple[str, ...]


def _violation(
    code: ViolationCode,
    field: str,
    message: str,
    fix_hint: str,
    *,
    severity: Severity = Severity.ERROR,
) -> Violation:
    return Violation(code=code, field=field, message=message, fix_hint=fix_hint, severity=severity)


def _parse_header(message: str) -> Header | None:
    header = message.split("\n", 1)[0].strip()
    parsed = grammar.split_title(header)
    if parsed is None:
        return None
    return Header(
        type=parsed["type"],
        scope=parsed.get("scope"),
        breaking=bool(parsed.get("breaking")),
        description=parsed["description"],
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


def _check_header(parsed: ParsedMessage, policy: _RulePolicy) -> Iterable[Violation]:
    header = parsed.header
    if header is None:
        yield _violation(
            ViolationCode.COMMIT_HEADER_FORMAT,
            "header",
            "Header does not match <type>[(<scope>)][!]: <description>",
            "Use the form 'type(scope)!: description' (scope and ! optional)",
        )
        return
    if header.type not in policy.types:
        yield _violation(
            ViolationCode.COMMIT_TYPE,
            "type",
            f"Commit type {header.type!r} is not allowed",
            f"Use one of: {', '.join(sorted(policy.types))}",
        )
    if not grammar.is_valid_description(header.description):
        yield _violation(
            ViolationCode.COMMIT_DESCRIPTION_FORMAT,
            "description",
            "Description must start with a lowercase letter or digit and use only lowercase characters",
            "Rewrite the description in lowercase, imperative, present tense",
        )
    if grammar.TRAILING_DOT.search(header.description):
        yield _violation(
            ViolationCode.COMMIT_DESCRIPTION_TRAILING_PERIOD,
            "description",
            "Description must not end with a period",
            "Remove the trailing period",
            severity=Severity.WARNING,
        )


def _check_title_length(parsed: ParsedMessage, policy: _RulePolicy) -> Iterable[Violation]:
    del policy
    title = parsed.message.split("\n", 1)[0]
    if grammar.title_length(title) > grammar.title_max_length():
        yield _violation(
            ViolationCode.COMMIT_TITLE_LENGTH,
            "title",
            f"Title exceeds {grammar.title_max_length()} characters",
            f"Shorten the title to at most {grammar.title_max_length()} characters",
        )


def _check_body_lines(parsed: ParsedMessage, policy: _RulePolicy) -> Iterable[Violation]:
    del policy
    for index, line in enumerate(_body_lines(parsed.message)):
        if len(line) > _BODY_LINE_MAX:
            yield _violation(
                ViolationCode.COMMIT_BODY_LINE_LENGTH,
                f"body[{index}]",
                f"Body line {index + 1} exceeds {_BODY_LINE_MAX} characters ({len(line)})",
                f"Wrap or shorten the line to at most {_BODY_LINE_MAX} characters",
            )
        if not _is_bullet(line):
            yield _violation(
                ViolationCode.COMMIT_BODY_BULLET,
                f"body[{index}]",
                f"Body line {index + 1} is not a bullet",
                "Prefix the line with '- ' or '* '",
                severity=Severity.WARNING,
            )


def _check_message_bytes(parsed: ParsedMessage, policy: _RulePolicy) -> Iterable[Violation]:
    del policy
    byte_length = len(parsed.message.encode("utf-8"))
    if byte_length > _MESSAGE_MAX_BYTES:
        yield _violation(
            ViolationCode.COMMIT_MESSAGE_BYTES,
            "message",
            f"Message exceeds {_MESSAGE_MAX_BYTES} bytes ({byte_length})",
            "Shorten the message so its UTF-8 encoding fits within the byte limit",
        )


def _check_breaking_footer(parsed: ParsedMessage, policy: _RulePolicy) -> Iterable[Violation]:
    del policy
    header = parsed.header
    if header is not None and header.breaking and not grammar.has_breaking_footer(parsed.message):
        yield _violation(
            ViolationCode.COMMIT_BREAKING_FOOTER,
            "footer",
            "Header marks a breaking change but no 'BREAKING CHANGE:' footer was found",
            "Append 'BREAKING CHANGE: <description>' after the body",
        )


def _check_attribution(parsed: ParsedMessage, policy: _RulePolicy) -> Iterable[Violation]:
    if not policy.attribution_patterns:
        return
    combined = re.compile("|".join(policy.attribution_patterns), re.IGNORECASE)
    message = parsed.message
    body_lines = message.split("\n", 1)[1].splitlines() if "\n" in message else []
    for index, line in enumerate(body_lines):
        stripped = line.strip()
        if stripped and combined.search(stripped):
            yield _violation(
                ViolationCode.COMMIT_ATTRIBUTION,
                f"footer[{index}]",
                f"Attribution line is not allowed: {stripped}",
                "Remove the attribution trailer",
            )


_CHECKS: Final[tuple[Callable[[ParsedMessage, _RulePolicy], Iterable[Violation]], ...]] = (
    _check_header,
    _check_title_length,
    _check_body_lines,
    _check_message_bytes,
    _check_breaking_footer,
    _check_attribution,
)


def validate_message(
    message: str,
    *,
    allowed_types: frozenset[str] | None = None,
    attribution_patterns: tuple[str, ...] | None = None,
) -> Report:
    if not message or not message.strip():
        return Report.from_violations(
            _violation(
                ViolationCode.COMMIT_EMPTY,
                "message",
                "Commit message is empty",
                "Provide a non-empty commit message",
            )
        )

    policy = _RulePolicy(
        types=allowed_types if allowed_types is not None else vocabulary.default_types(),
        attribution_patterns=vocabulary.default_attribution_patterns() + (attribution_patterns or ()),
    )
    parsed = ParsedMessage(message=message, header=_parse_header(message))
    violations = [violation for check in _CHECKS for violation in check(parsed, policy)]
    return Report.from_violations(*violations)


def message_max_bytes() -> int:
    return _MESSAGE_MAX_BYTES


def body_line_max() -> int:
    return _BODY_LINE_MAX
