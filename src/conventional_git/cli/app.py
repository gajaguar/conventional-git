from __future__ import annotations

import contextlib
from importlib import import_module

import typer

from conventional_git.cli import auth as auth_module
from conventional_git.cli import capabilities as capabilities_module
from conventional_git.cli import check as check_module
from conventional_git.cli import create as create_module
from conventional_git.cli import hook as hook_module

# pylint: disable-next=app-require-final,app-module-const-naming
app = typer.Typer(
    name="conventional-git",
    help="Validate, enforce, and generate Conventional Commits / Conventional Branch names.",
    no_args_is_help=True,
)

app.add_typer(auth_module.app, name="auth")
app.add_typer(capabilities_module.app, name="capabilities")
app.add_typer(check_module.app, name="check")
app.add_typer(create_module.app, name="create")
app.add_typer(hook_module.app, name="hook")

# The `mcp` extra pulls in a heavy dependency tree (pydantic, httpx,
# starlette, ...) that most CLI/hook-only installs don't need, so the
# subcommand only appears when `conventional-git[mcp]` is installed.
with contextlib.suppress(ImportError):
    # pylint: disable-next=app-require-final,app-module-const-naming
    mcp_module = import_module("conventional_git.cli.mcp")
    app.add_typer(mcp_module.app, name="mcp")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
