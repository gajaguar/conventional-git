from __future__ import annotations

import contextlib
from dataclasses import dataclass
from importlib import import_module
from typing import Protocol


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
    ) -> CommitSuggestion | None: ...


class MissingCredentialsError(RuntimeError):
    pass


_REGISTRY: dict[str, SuggestionProvider] = {}


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
