from __future__ import annotations

import typer

from conventional_kit.mcp import server

app = typer.Typer(help="MCP server surface for conventional-kit.")


@app.command("serve")
def serve() -> None:
    server.run()
