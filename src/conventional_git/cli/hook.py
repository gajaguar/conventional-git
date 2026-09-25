from __future__ import annotations

import subprocess  # ruff: ignore[suspicious-subprocess-import]
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Annotated

import typer

if TYPE_CHECKING:
    from typing import Final

# pylint: disable-next=app-require-final,app-module-const-naming
app = typer.Typer(help="Install / uninstall pre-commit hooks in any git repo.")


_MANAGED_BY: Final[str] = "# managed-by: conventional-git"
_HOOK_NAMES: Final[tuple[str, ...]] = ("commit-msg", "pre-commit", "pre-push")


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
    hooks_dir = _hooks_dir(cwd)
    hooks_dir.mkdir(parents=True, exist_ok=True)
    _note_for_external_hooks_dir(cwd, hooks_dir)
    _write_hook(
        hooks_dir / "commit-msg",
        f'#!/usr/bin/env bash\n{_MANAGED_BY}\nset -euo pipefail\nconventional-git check commit --file "$1"\n',
        force=force,
    )
    _write_hook(
        hooks_dir / "pre-commit",
        "#!/usr/bin/env bash\n"
        f"{_MANAGED_BY}\n"
        "set -euo pipefail\n"
        "# detached HEAD: no branch to validate\n"
        "current=$(git symbolic-ref --quiet --short HEAD) || exit 0\n"
        'conventional-git check branch --name "$current"\n',
        force=force,
    )
    _write_hook(
        hooks_dir / "pre-push",
        "#!/usr/bin/env bash\n"
        f"{_MANAGED_BY}\n"
        "set -euo pipefail\n"
        "while read -r local_ref local_sha remote_ref remote_sha; do\n"
        '  [ -z "$local_sha" ] && continue\n'
        '  [ "$local_sha" = "0000000000000000000000000000000000000000" ] && continue\n'
        "  branch=${local_ref#refs/heads/}\n"
        '  conventional-git check branch --name "$branch" < /dev/null\n'
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
    hooks_dir = _hooks_dir(cwd)
    for name in _HOOK_NAMES:
        path = hooks_dir / name
        if not path.exists():
            continue
        if _MANAGED_BY not in path.read_text(encoding="utf-8"):
            typer.echo(f"Skipping {path}: not installed by conventional-git")
            continue
        path.unlink()
    typer.echo(f"Removed hooks from {hooks_dir}")


def _hooks_dir(repo: Path) -> Path:
    result = subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true] — fixed argv, no shell, no user-controlled input
        ["git", "-C", str(repo), "rev-parse", "--git-path", "hooks"],  # ruff: ignore[start-process-with-partial-path]
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        typer.echo(f"Not a git repository: {repo}", err=True)
        raise typer.Exit(1)
    hooks_dir = Path(result.stdout.strip())
    return hooks_dir if hooks_dir.is_absolute() else repo / hooks_dir


def _note_for_external_hooks_dir(repo: Path, hooks_dir: Path) -> None:
    result = subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true] — fixed argv, no shell, no user-controlled input
        ["git", "-C", str(repo), "rev-parse", "--git-common-dir"],  # ruff: ignore[start-process-with-partial-path]
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        return
    git_common_dir = Path(result.stdout.strip())
    if not git_common_dir.is_absolute():
        git_common_dir = repo / git_common_dir
    default_hooks_dir = (git_common_dir / "hooks").resolve()
    if hooks_dir.resolve() != default_hooks_dir:
        typer.echo(
            f"Note: hooks path {hooks_dir} is outside {default_hooks_dir}; it may be managed by another tool.",
        )


def _write_hook(path: Path, content: str, *, force: bool) -> None:
    if path.exists() and not force:
        typer.echo(f"Refusing to overwrite existing hook: {path}", err=True)
        raise typer.Exit(1)
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)
