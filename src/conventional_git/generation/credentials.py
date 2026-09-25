from __future__ import annotations

import contextlib
import os
from dataclasses import dataclass
from typing import TYPE_CHECKING

import keyring
from keyring.errors import KeyringError

from conventional_git.generation.protocol import MissingCredentialsError

if TYPE_CHECKING:
    from typing import Final

_SERVICE: Final[str] = "conventional-git"

# Order doubles as resolution priority: env vars are checked in this order,
# then the keyring entries are checked in this same order.
PROVIDERS: Final[tuple[str, ...]] = ("typesafe", "openrouter")

_ENV_VARS: Final[dict[str, str]] = {
    "typesafe": "TYPESAFE_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
}


@dataclass(frozen=True, slots=True)
class Credential:
    provider: str
    key: str
    source: str  # "env" or "keyring"


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
        return Credential(provider=provider, key=key, source="env")
    key = stored_key(provider)
    if key:
        return Credential(provider=provider, key=key, source="keyring")
    return None


def resolve_active_credential() -> Credential | None:
    for provider in PROVIDERS:
        key = env_key(provider)
        if key:
            return Credential(provider=provider, key=key, source="env")
    for provider in PROVIDERS:
        key = stored_key(provider)
        if key:
            return Credential(provider=provider, key=key, source="keyring")
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
