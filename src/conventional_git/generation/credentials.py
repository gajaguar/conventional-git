from __future__ import annotations

import contextlib
import os
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

import keyring
from keyring.errors import KeyringError

from conventional_git.generation.protocol import MissingCredentialsError

if TYPE_CHECKING:
    from typing import Final

_SERVICE: Final[str] = "conventional-git"


class CredentialProvider(StrEnum):
    # Definition order doubles as resolution priority: env vars are checked
    # in this order, then the keyring entries are checked in this same order.
    TYPESAFE = "typesafe"
    OPENROUTER = "openrouter"

    @property
    def display_name(self) -> str:
        return _DISPLAY_NAMES[self]


class CredentialSource(StrEnum):
    ENV = "env"
    KEYRING = "keyring"


_ENV_VARS: Final[dict[str, str]] = {
    CredentialProvider.TYPESAFE: "TYPESAFE_API_KEY",
    CredentialProvider.OPENROUTER: "OPENROUTER_API_KEY",
}
_DISPLAY_NAMES: Final[dict[str, str]] = {
    CredentialProvider.TYPESAFE: "TypeSafe",
    CredentialProvider.OPENROUTER: "OpenRouter",
}

PROVIDERS: Final[tuple[CredentialProvider, ...]] = tuple(CredentialProvider)


@dataclass(frozen=True, slots=True)
class Credential:
    provider: str
    key: str
    source: CredentialSource


def env_var_name(provider: str) -> str:
    return _ENV_VARS[provider]


def env_key(provider: str) -> str | None:
    key = os.environ.get(env_var_name(provider), "").strip()
    return key or None


def stored_key(provider: str) -> str | None:
    with contextlib.suppress(KeyringError):
        key = keyring.get_password(_SERVICE, provider)
        return key.strip() if key and key.strip() else None
    return None


def resolve_credential(provider: str) -> Credential | None:
    key = env_key(provider)
    if key:
        return Credential(provider=provider, key=key, source=CredentialSource.ENV)
    key = stored_key(provider)
    if key:
        return Credential(provider=provider, key=key, source=CredentialSource.KEYRING)
    return None


def resolve_active_credential() -> Credential | None:
    for provider in PROVIDERS:
        key = env_key(provider)
        if key:
            return Credential(provider=provider, key=key, source=CredentialSource.ENV)
    for provider in PROVIDERS:
        key = stored_key(provider)
        if key:
            return Credential(provider=provider, key=key, source=CredentialSource.KEYRING)
    return None


def store_key(provider: str, key: str) -> None:
    if provider not in PROVIDERS:
        message = f"Unknown provider {provider!r}"
        raise ValueError(message)
    try:
        keyring.set_password(_SERVICE, provider, key)
    except KeyringError as error:
        message = (
            f"No usable OS keyring backend is available: {error}. "
            f"Set {env_var_name(provider)} in the environment instead."
        )
        raise MissingCredentialsError(message) from error


def clear_key(provider: str) -> None:
    if provider not in PROVIDERS:
        message = f"Unknown provider {provider!r}"
        raise ValueError(message)
    with contextlib.suppress(KeyringError):
        keyring.delete_password(_SERVICE, provider)
