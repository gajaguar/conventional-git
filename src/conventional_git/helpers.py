from __future__ import annotations

import re
from typing import TYPE_CHECKING

from conventional_git.commit import vocabulary as commit_vocabulary
from conventional_git.config import Config

if TYPE_CHECKING:
    from typing import Final

# Stripping (used by `create commit`) is intentionally broader than the
# `commit.attribution` validation rule: it also removes bare mentions of the
# generating tool/vendor, which would be false positives if rejected outright.
_GENERATOR_ONLY_PATTERNS: Final[tuple[str, ...]] = ("claude", "anthropic")
DEFAULT_ATTRIBUTION_PATTERN: Final[re.Pattern[str]] = re.compile(
    "|".join((*commit_vocabulary.default_attribution_patterns(), *_GENERATOR_ONLY_PATTERNS)),
    re.IGNORECASE,
)


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
