from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

app = typer.Typer(help="Install / uninstall pre-commit hooks in any git repo.")


_HOOK_DIR = Path(".git/hooks")


def _repo_root() -> Path:
    return Path.cwd()


@app.command("install")
def install_hook(
    target: Annotated[
        Path | None,
        typer.Option(
            "--target",
            help="Target repo path; defaults to the current directory",
        ),
    ] = None,
    force: Annotated[
        bool,
        typer.Option(
            "--force/--no-force",
            help="Overwrite existing hooks if present",
        ),
    ] = False,
) -> None:
    cwd = (target or _repo_root()).resolve()
    hooks_dir = cwd / ".git" / "hooks"
    if not hooks_dir.parent.exists():
        typer.echo(f"No .git directory found at {cwd}", err=True)
        raise typer.Exit(1)
    hooks_dir.mkdir(exist_ok=True)
    _write_hook(
        hooks_dir / "commit-msg",
        '#!/usr/bin/env bash\nset -euo pipefail\nconventional-kit check commit --file "$1"\n',
        force=force,
    )
    _write_hook(
        hooks_dir / "pre-commit",
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "current=$(git rev-parse --abbrev-ref HEAD)\n"
        'conventional-kit check branch --name "$current"\n',
        force=force,
    )
    _write_hook(
        hooks_dir / "pre-push",
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "while read -r local_ref local_sha remote_ref remote_sha; do\n"
        '  [ -z "$local_sha" ] && continue\n'
        '  [ "$local_sha" = "0000000000000000000000000000000000000000" ] && continue\n'
        "  branch=${local_ref#refs/heads/}\n"
        '  conventional-kit check branch --name "$branch" < /dev/null\n'
        "done\n",
        force=force,
    )
    typer.echo(f"Installed hooks in {hooks_dir}")


@app.command("uninstall")
def uninstall_hook(
    target: Annotated[
        Path | None,
        typer.Option("--target", help="Target repo path; defaults to the current directory"),
    ] = None,
) -> None:
    cwd = (target or _repo_root()).resolve()
    hooks_dir = cwd / ".git" / "hooks"
    for name in ("commit-msg", "pre-commit", "pre-push"):
        path = hooks_dir / name
        if path.exists():
            path.unlink()
    typer.echo(f"Removed hooks from {hooks_dir}")


def _write_hook(path: Path, content: str, *, force: bool) -> None:
    if path.exists() and not force:
        typer.echo(f"Refusing to overwrite existing hook: {path}", err=True)
        raise typer.Exit(1)
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)
