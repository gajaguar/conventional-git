from __future__ import annotations

import typer

from conventional_git.cli import auth as auth_module
from conventional_git.cli import check as check_module
from conventional_git.cli import create as create_module
from conventional_git.cli import hook as hook_module
from conventional_git.cli import mcp as mcp_module

app = typer.Typer(
    name="conventional-git",
    help="Validate, enforce, and generate Conventional Commits / Conventional Branch names.",
    no_args_is_help=True,
)

app.add_typer(auth_module.app, name="auth")
app.add_typer(check_module.app, name="check")
app.add_typer(create_module.app, name="create")
app.add_typer(hook_module.app, name="hook")
app.add_typer(mcp_module.app, name="mcp")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
