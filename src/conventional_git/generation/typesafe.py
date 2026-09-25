from __future__ import annotations

import os
from typing import TYPE_CHECKING

from typesafe_sdk import Choice
from typesafe_sdk import Noul
from typesafe_sdk import TypeSafeClient
from typesafe_sdk import TypeSafeError

from conventional_git.commit import grammar as commit_grammar
from conventional_git.commit import vocabulary as commit_vocab
from conventional_git.generation import credentials
from conventional_git.generation.diff import change_verb
from conventional_git.generation.diff import parse_diff
from conventional_git.generation.diff import paths_from_diff
from conventional_git.generation.heuristic import infer_description
from conventional_git.generation.heuristic import infer_type
from conventional_git.generation.protocol import CommitSuggestion
from conventional_git.generation.protocol import MissingCredentialsError
from conventional_git.generation.protocol import ProviderError
from conventional_git.generation.protocol import register_provider

if TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Mapping
    from typing import Final

_DIFF_MAX_CHARS: Final[int] = 12_000
_BASE_URL_ENV: Final[str] = "TYPESAFE_BASE_URL"
_MODEL_ENV: Final[str] = "TYPESAFE_DEFAULT_MODEL"
_OPENROUTER_BASE_URL: Final[str] = "https://openrouter.ai/api"
_OPENROUTER_MODEL: Final[str] = "typesafe/jev-1.13"
_NO_SCOPE: Final[str] = "none"
_BREAKING_THRESHOLD: Final[float] = 0.5


def _scope_candidates(paths: tuple[str, ...], types: Mapping[str, str]) -> list[str]:
    seen: dict[str, None] = {}
    for path in paths:
        head = path.split("/", 1)[0] if "/" in path else ""
        if head and head not in types and commit_grammar.is_valid_scope(head) and head not in seen:
            seen[head] = None
    return [*seen, _NO_SCOPE]


def _description_candidates(paths: tuple[str, ...], commit_type: str, diff: str) -> list[str]:
    verb = change_verb(parse_diff(diff))
    leaf = paths[0].rsplit("/", 1)[-1]
    candidates = {infer_description(paths, commit_type, verb), f"{verb} {leaf}"}
    return sorted(candidates)


def _build_client() -> TypeSafeClient:
    typesafe_key = credentials.resolve_typesafe_key()
    if typesafe_key:
        return TypeSafeClient(api_key=typesafe_key)
    openrouter_key = credentials.resolve_openrouter_key()
    if not openrouter_key:
        message = "No TypeSafe or OpenRouter API key found. Run 'conventional-git auth login'."
        raise MissingCredentialsError(message)
    base_url = os.environ.get(_BASE_URL_ENV, "").strip() or _OPENROUTER_BASE_URL
    model = os.environ.get(_MODEL_ENV, "").strip() or _OPENROUTER_MODEL
    return TypeSafeClient(api_key=openrouter_key, base_url=base_url, model=model)


class JevProvider:
    name = "jev"

    def __init__(self, client_factory: Callable[[], TypeSafeClient] = _build_client) -> None:
        self._client_factory = client_factory

    def suggest(
        self,
        diff: str,
        *,
        changed_paths: tuple[str, ...] = (),
        types: Mapping[str, str] | None = None,
    ) -> CommitSuggestion | None:
        paths = changed_paths or paths_from_diff(diff)
        if not paths:
            return None
        criteria = dict(types) if types else commit_vocab.default_criteria()
        allowed_types = set(criteria)
        fallback_type = infer_type(paths)
        scope_candidates = _scope_candidates(paths, criteria)
        description_candidates = _description_candidates(paths, fallback_type, diff)
        truncated_diff = diff[:_DIFF_MAX_CHARS]

        try:
            client = self._client_factory()
            with client:
                response = client.system_one(
                    state={"diff": truncated_diff, "changed_paths": list(paths)},
                    questions={
                        "type": Choice(
                            instructions="Which Conventional Commits type best matches this diff?",
                            criteria=criteria,
                        ),
                        "scope": Choice(
                            instructions=(
                                "Pick the single module or area most affected by this diff, "
                                f"or {_NO_SCOPE!r} if it spans several unrelated areas."
                            ),
                            criteria=dict.fromkeys(scope_candidates),
                        ),
                        "description": Choice(
                            instructions=(
                                "Pick the imperative, present-tense commit description that best summarizes this diff."
                            ),
                            criteria=dict.fromkeys(description_candidates),
                        ),
                        "breaking": Noul(
                            instructions=(
                                "Does this diff remove or incompatibly change a public interface "
                                "(a public function signature, CLI flag, or API response shape)?"
                            ),
                        ),
                    },
                )
        except TypeSafeError as error:
            message = f"jev provider failed: {type(error).__name__}: {error}"
            raise ProviderError(message) from error

        type_answer = response.choices["type"]
        commit_type = type_answer.choice if type_answer.choice in allowed_types else fallback_type
        scope_choice = response.choices["scope"].choice
        return CommitSuggestion(
            type=commit_type,
            scope="" if scope_choice == _NO_SCOPE else scope_choice,
            description=response.choices["description"].choice,
            confidence=type_answer.confidence,
            breaking=response.nouls["breaking"].noul >= _BREAKING_THRESHOLD,
        )


register_provider(JevProvider())
