from __future__ import annotations

import typer

from conventional_git.mcp import server

# pylint: disable-next=app-require-final,app-module-const-naming
app = typer.Typer(help="MCP server surface for conventional-git.")


@app.command("serve")
def serve() -> None:
    server.run()
