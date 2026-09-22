from __future__ import annotations

import re
from pathlib import Path
from typing import Final
from typing import NoReturn

import typer

from conventional_git.commit import vocabulary as commit_vocabulary
from conventional_git.config import Config

# Stripping (used by `create commit`) is intentionally broader than the
# `commit.attribution` validation rule: it also removes bare mentions of the
# generating tool/vendor, which would be false positives if rejected outright.
_GENERATOR_ONLY_PATTERNS: Final[tuple[str, ...]] = ("claude", "anthropic")
DEFAULT_ATTRIBUTION_PATTERN: Final[re.Pattern[str]] = re.compile(
    "|".join((*commit_vocabulary.default_attribution_patterns(), *_GENERATOR_ONLY_PATTERNS)),
    re.IGNORECASE,
)
MAX_BODY_LINE_LENGTH: Final[int] = 140
MAX_MESSAGE_BYTES: Final[int] = 2048


def _compile(config: Config) -> re.Pattern[str]:
    if not config.extra_attribution_patterns:
        return DEFAULT_ATTRIBUTION_PATTERN
    parts = [DEFAULT_ATTRIBUTION_PATTERN.pattern, *config.extra_attribution_patterns]
    return re.compile("|".join(parts), re.IGNORECASE)


def strip_attribution(raw: str | None, *, config: Config | None = None) -> list[str]:
    if not raw:
        return []
    pattern = _compile(config or Config.load())
    lines: list[str] = []
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or pattern.search(stripped):
            continue
        lines.append(stripped)
    return lines


def check_body_line_length(line: str) -> None:
    if len(line) > MAX_BODY_LINE_LENGTH:
        fail(f"Body line exceeds {MAX_BODY_LINE_LENGTH} characters ({len(line)}): {line}")


def fail(message: str) -> NoReturn:
    typer.echo(message, err=True)
    raise SystemExit(1)


def message_max_bytes() -> int:
    return MAX_MESSAGE_BYTES


def body_line_max() -> int:
    return MAX_BODY_LINE_LENGTH


def load_config(path: str | Path | None = None) -> Config:
    if path is None:
        return Config.load()
    return Config.load(Path(path))
