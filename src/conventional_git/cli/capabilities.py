from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as package_version
from importlib.util import find_spec
from typing import TYPE_CHECKING
from typing import Annotated

import typer

from conventional_git import generation

try:
    from conventional_git.generation import credentials
except ImportError:
    # pylint: disable-next=app-require-final,app-module-const-naming
    credentials = None  # type: ignore[assignment]

try:
    from conventional_git.mcp import server as mcp_server
except ImportError:
    # pylint: disable-next=app-require-final,app-module-const-naming
    mcp_server = None  # type: ignore[assignment]

if TYPE_CHECKING:
    from typing import Final

# pylint: disable-next=app-require-final,app-module-const-naming
app = typer.Typer(help="Report what this installed conventional-git supports.")

_PACKAGE_NAME: Final[str] = "conventional-git"


@dataclass(frozen=True, slots=True)
class Capabilities:
    version: str
    extras: dict[str, bool]
    providers: tuple[str, ...]
    credentials: dict[str, str | None]
    mcp_tools: tuple[str, ...]


def _resolve_version() -> str:
    try:
        return package_version(_PACKAGE_NAME)
    except PackageNotFoundError:
        return "unknown"


def _resolve_extras() -> dict[str, bool]:
    return {
        "llm": find_spec("keyring") is not None and find_spec("typesafe_sdk") is not None,
        "mcp": mcp_server is not None,
        "gitlint": find_spec("gitlint") is not None,
    }


def _resolve_credentials(*, has_llm: bool) -> dict[str, str | None]:
    if not has_llm or credentials is None:
        return {}
    result: dict[str, str | None] = {}
    for provider in credentials.PROVIDERS:
        credential = credentials.resolve_credential(provider)
        result[provider] = credential.source if credential is not None else None
    return result


def _resolve_mcp_tools(*, has_mcp: bool) -> tuple[str, ...]:
    if not has_mcp or mcp_server is None:
        return ()
    tools = asyncio.run(mcp_server.mcp.list_tools())
    return tuple(tool.name for tool in tools)


def collect() -> Capabilities:
    extras = _resolve_extras()
    generation.enable_optional_providers()
    return Capabilities(
        version=_resolve_version(),
        extras=extras,
        providers=generation.available_providers(),
        credentials=_resolve_credentials(has_llm=extras["llm"]),
        mcp_tools=_resolve_mcp_tools(has_mcp=extras["mcp"]),
    )


@app.callback(invoke_without_command=True)
def capabilities(
    as_json: Annotated[bool, typer.Option("--json", help="Print machine-readable JSON")] = False,
) -> None:
    report = collect()
    if as_json:
        payload = {
            "version": report.version,
            "extras": report.extras,
            "providers": list(report.providers),
            "credentials": report.credentials,
            "mcp_tools": list(report.mcp_tools),
        }
        typer.echo(json.dumps(payload))
        return
    typer.echo(f"version: {report.version}")
    typer.echo(f"extras: {', '.join(f'{name}={value}' for name, value in report.extras.items())}")
    typer.echo(f"providers: {', '.join(report.providers) or '(none)'}")
    for provider, source in report.credentials.items():
        typer.echo(f"credential[{provider}]: {source or 'not set'}")
    if report.mcp_tools:
        typer.echo(f"mcp_tools: {', '.join(report.mcp_tools)}")
