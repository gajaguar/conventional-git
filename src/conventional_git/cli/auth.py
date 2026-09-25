from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Annotated

import typer

from conventional_git.generation.protocol import MissingCredentialsError

try:
    from conventional_git.generation import credentials
except ImportError:
    # pylint: disable-next=app-require-final,app-module-const-naming
    credentials = None  # type: ignore[assignment]

if TYPE_CHECKING:
    from types import ModuleType
    from typing import Final

# pylint: disable-next=app-require-final,app-module-const-naming
app = typer.Typer(help="Manage credentials for LLM-backed suggestion providers (requires the 'llm' extra).")

_INSTALL_HINT: Final[str] = "Install the LLM extra first: pip install 'conventional-git[llm]'"
_MASK_MIN_VISIBLE_LENGTH: Final[int] = 4
_DISPLAY_NAMES: Final[dict[str, str]] = {
    "typesafe": "TypeSafe",
    "openrouter": "OpenRouter",
}


def _require_credentials() -> ModuleType:
    if credentials is None:
        typer.echo(_INSTALL_HINT, err=True)
        raise typer.Exit(1)
    return credentials


def _require_provider(creds: ModuleType, provider: str) -> None:
    if provider not in creds.PROVIDERS:
        available = ", ".join(creds.PROVIDERS)
        typer.echo(f"Unknown provider {provider!r}. Available: {available}", err=True)
        raise typer.Exit(2)


@app.command("login")
def login(
    provider: Annotated[
        str,
        typer.Option("--provider", help="Which provider to store a key for (typesafe or openrouter)"),
    ] = "openrouter",
) -> None:
    creds = _require_credentials()
    _require_provider(creds, provider)
    key = typer.prompt(f"{_DISPLAY_NAMES[provider]} API key", hide_input=True)
    if not key.strip():
        typer.echo("Refusing to store an empty key.", err=True)
        raise typer.Exit(1)
    try:
        creds.store_key(provider, key.strip())
    except MissingCredentialsError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(1) from error
    typer.echo(f"Stored the {_DISPLAY_NAMES[provider]} API key in the OS keyring.")


@app.command("status")
def status() -> None:
    creds = _require_credentials()
    active = creds.resolve_active_credential()
    found_any = False
    for provider in creds.PROVIDERS:
        credential = creds.resolve_credential(provider)
        name = _DISPLAY_NAMES[provider]
        if credential is None:
            typer.echo(f"{name}: not set")
            continue
        found_any = True
        env_var = creds.env_var_name(provider)
        source = f"env ({env_var})" if credential.source == "env" else "keyring"
        marker = " (active)" if active is not None and active.provider == provider else ""
        typer.echo(f"{name}: {source}, {_mask(credential.key)}{marker}")
    if not found_any:
        typer.echo("No credentials found. Run 'conventional-git auth login'.")


@app.command("logout")
def logout(
    provider: Annotated[
        str | None,
        typer.Option("--provider", help="Which provider's stored key to remove (default: all)"),
    ] = None,
) -> None:
    creds = _require_credentials()
    if provider is None:
        for name in creds.PROVIDERS:
            creds.clear_key(name)
        typer.echo("Removed all stored API keys.")
        return
    _require_provider(creds, provider)
    creds.clear_key(provider)
    typer.echo(f"Removed the stored {_DISPLAY_NAMES[provider]} API key.")


def _mask(key: str) -> str:
    if len(key) <= _MASK_MIN_VISIBLE_LENGTH:
        return "*" * len(key)
    return f"{'*' * (len(key) - _MASK_MIN_VISIBLE_LENGTH)}{key[-_MASK_MIN_VISIBLE_LENGTH:]}"
