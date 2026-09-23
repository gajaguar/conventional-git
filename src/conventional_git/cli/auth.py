from __future__ import annotations

from typing import TYPE_CHECKING

import typer

from conventional_git.generation.protocol import MissingCredentialsError

try:
    from conventional_git.generation import credentials
except ImportError:
    credentials = None  # type: ignore[assignment]

if TYPE_CHECKING:
    from types import ModuleType

app = typer.Typer(help="Manage credentials for LLM-backed suggestion providers (requires the 'llm' extra).")

_INSTALL_HINT = "Install the LLM extra first: pip install 'conventional-git[llm]'"
_MASK_MIN_VISIBLE_LENGTH = 4


def _require_credentials() -> ModuleType:
    if credentials is None:
        typer.echo(_INSTALL_HINT, err=True)
        raise typer.Exit(1)
    return credentials


@app.command("login")
def login() -> None:
    creds = _require_credentials()
    key = typer.prompt("OpenRouter API key", hide_input=True)
    if not key.strip():
        typer.echo("Refusing to store an empty key.", err=True)
        raise typer.Exit(1)
    try:
        creds.store_openrouter_key(key.strip())
    except MissingCredentialsError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(1) from error
    typer.echo("Stored the OpenRouter API key in the OS keyring.")


@app.command("status")
def status() -> None:
    creds = _require_credentials()
    typesafe_key = creds.resolve_typesafe_key()
    if typesafe_key:
        typer.echo(f"TypeSafe key: env (TYPESAFE_API_KEY), {_mask(typesafe_key)}")
        return
    openrouter_key = creds.resolve_openrouter_key()
    if openrouter_key:
        typer.echo(f"OpenRouter key: available, {_mask(openrouter_key)}")
        return
    typer.echo("No credentials found. Run 'conventional-git auth login'.")


@app.command("logout")
def logout() -> None:
    creds = _require_credentials()
    creds.clear_openrouter_key()
    typer.echo("Removed the stored OpenRouter API key.")


def _mask(key: str) -> str:
    if len(key) <= _MASK_MIN_VISIBLE_LENGTH:
        return "*" * len(key)
    return f"{'*' * (len(key) - _MASK_MIN_VISIBLE_LENGTH)}{key[-_MASK_MIN_VISIBLE_LENGTH:]}"
