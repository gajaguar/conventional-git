from __future__ import annotations

import contextlib
import os
from typing import Final

import keyring
from keyring.errors import KeyringError

from conventional_git.generation.protocol import MissingCredentialsError

_SERVICE: Final[str] = "conventional-git"
_TYPESAFE_ENV: Final[str] = "TYPESAFE_API_KEY"
_OPENROUTER_ENV: Final[str] = "OPENROUTER_API_KEY"
_OPENROUTER_KEYRING_USER: Final[str] = "openrouter"


def resolve_typesafe_key() -> str | None:
    key = os.environ.get(_TYPESAFE_ENV, "").strip()
    return key or None


def resolve_openrouter_key() -> str | None:
    key = os.environ.get(_OPENROUTER_ENV, "").strip()
    if key:
        return key
    with contextlib.suppress(KeyringError):
        return keyring.get_password(_SERVICE, _OPENROUTER_KEYRING_USER)
    return None


def store_openrouter_key(key: str) -> None:
    try:
        keyring.set_password(_SERVICE, _OPENROUTER_KEYRING_USER, key)
    except KeyringError as error:
        message = f"No usable OS keyring backend is available: {error}"
        raise MissingCredentialsError(message) from error


def clear_openrouter_key() -> None:
    with contextlib.suppress(KeyringError):
        keyring.delete_password(_SERVICE, _OPENROUTER_KEYRING_USER)
