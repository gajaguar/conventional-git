from __future__ import annotations

import contextlib
from dataclasses import dataclass
from importlib import import_module
from typing import TYPE_CHECKING
from typing import Protocol

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Final


@dataclass(frozen=True, slots=True)
class CommitSuggestion:
    type: str
    scope: str
    description: str
    confidence: float
    breaking: bool = False


class SuggestionProvider(Protocol):
    name: str

    def suggest(
        self,
        diff: str,
        *,
        changed_paths: tuple[str, ...] = (),
        types: Mapping[str, str] | None = None,
    ) -> CommitSuggestion | None: ...


class ProviderError(RuntimeError):
    pass


class MissingCredentialsError(ProviderError):
    pass


_REGISTRY: Final[dict[str, SuggestionProvider]] = {}


def register_provider(provider: SuggestionProvider) -> None:
    _REGISTRY[provider.name] = provider


def get_provider(name: str | None = None) -> SuggestionProvider | None:
    if name is None:
        name = "heuristic"
    return _REGISTRY.get(name)


def available_providers() -> tuple[str, ...]:
    return tuple(_REGISTRY.keys())


def enable_optional_providers() -> None:
    with contextlib.suppress(ImportError):
        import_module("conventional_git.generation.typesafe")


@dataclass(frozen=True, slots=True)
class SuggestionResult:
    provider: str | None
    suggestion: CommitSuggestion | None
    warning: str | None = None
    error: str | None = None


def suggest(
    diff: str,
    *,
    changed_paths: tuple[str, ...] = (),
    types: Mapping[str, str] | None = None,
    preferred: str | None = None,
) -> SuggestionResult:
    enable_optional_providers()
    name = preferred or ("jev" if "jev" in available_providers() else "heuristic")
    provider = get_provider(name)
    if provider is None:
        error = f"Unknown provider {name!r}. Available: {', '.join(available_providers())}"
        return SuggestionResult(provider=None, suggestion=None, error=error)
    try:
        suggestion = provider.suggest(diff, changed_paths=changed_paths, types=types)
    except ProviderError as error:
        if preferred is not None:
            return SuggestionResult(provider=name, suggestion=None, error=str(error))
        heuristic = get_provider("heuristic")
        fallback = heuristic.suggest(diff, changed_paths=changed_paths, types=types) if heuristic else None
        return SuggestionResult(provider="heuristic", suggestion=fallback, warning=str(error))
    return SuggestionResult(provider=name, suggestion=suggestion)
