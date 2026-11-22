from __future__ import annotations

import json
import re
import shlex
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Final

_PR_COMMANDS: Final[frozenset[tuple[str, str, str]]] = frozenset({
    ("gh", "pr", "create"),
    ("gh", "pr", "edit"),
    ("bitbucket", "pr", "create"),
    ("bitbucket", "pr", "update"),
})
_OPERATORS: Final[frozenset[str]] = frozenset({"&&", "||", ";", "|", "&", "(", ")"})
_ASSIGNMENT: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z_]\w*=")
_HEREDOC: Final[re.Pattern[str]] = re.compile(r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n(.*?)\n[ \t]*\2(?=\s|$|\)|;)", re.DOTALL)
_TEXT_FLAGS: Final[frozenset[str]] = frozenset({"--body", "-b", "--title", "-t"})
_FILE_FLAGS: Final[frozenset[str]] = frozenset({"--body-file", "-F"})


def command_from_payload(raw: str) -> str:
    try:
        payload = json.loads(raw)
    except ValueError:
        return raw
    if isinstance(payload, dict):
        tool_input = payload.get("tool_input")
        command = tool_input.get("command") if isinstance(tool_input, dict) else None
        if isinstance(command, str):
            return command
    return raw


def _segments(tokens: list[str]) -> list[list[str]]:
    segments: list[list[str]] = [[]]
    for token in tokens:
        if token in _OPERATORS:
            segments.append([])
        else:
            segments[-1].append(token)
    return segments


def _without_assignments(segment: list[str]) -> list[str]:
    start = 0
    while start < len(segment) and _ASSIGNMENT.match(segment[start]):
        start += 1
    return segment[start:]


def _read(path: str) -> str | None:
    if path == "-":
        return None
    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError, UnicodeDecodeError:
        return None


def _segment_texts(words: list[str]) -> list[str]:
    texts: list[str] = []
    for index, word in enumerate(words):
        flag, equals, inline = word.partition("=")
        value = inline if equals else (words[index + 1] if index + 1 < len(words) else None)
        if value is None:
            continue
        if flag in _TEXT_FLAGS:
            texts.append(value)
        elif flag in _FILE_FLAGS and (content := _read(value)) is not None:
            texts.append(content)
    return texts


def pr_texts(command: str) -> list[str]:
    heredocs = [match.group(3) for match in _HEREDOC.finditer(command)]
    remainder = _HEREDOC.sub(lambda match: match.group(0).split("\n", 1)[0] + "\n" + match.group(2), command)
    lexer = shlex.shlex(remainder, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    try:
        tokens = list(lexer)
    except ValueError:
        return []
    texts: list[str] = []
    matched = False
    for segment in _segments(tokens):
        words = _without_assignments(segment)
        if tuple(words[:3]) in _PR_COMMANDS:
            matched = True
            texts.extend(_segment_texts(words[3:]))
    return texts + heredocs if matched else []
