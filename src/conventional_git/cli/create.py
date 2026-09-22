from __future__ import annotations

from pathlib import Path  # noqa: TC003 — Typer resolves at runtime
from typing import Annotated

import typer

from conventional_git.branch import rules as branch_rules
from conventional_git.branch import vocabulary as branch_vocab
from conventional_git.commit import grammar as commit_grammar
from conventional_git.commit import rules as commit_rules
from conventional_git.commit import vocabulary as commit_vocab
from conventional_git.config import Config
from conventional_git.helpers import strip_attribution

app = typer.Typer(help="Generate a Conventional Commits message or branch name from inputs.")


@app.command("commit")
def create_commit(
    commit_type: Annotated[str, typer.Option("--type", help="Conventional commit type (e.g. feat, fix)")],
    description: Annotated[
        str, typer.Option("--description", help="Imperative present-tense summary, lowercase first letter")
    ],
    scope: Annotated[
        str | None,
        typer.Option(help="Optional scope; a single lowercase token (auth, api, cli)"),
    ] = None,
    body: Annotated[
        str | None,
        typer.Option(help="Entire body as one newline-separated string"),
    ] = None,
    breaking: Annotated[
        bool,
        typer.Option("--breaking/--no-breaking", help="Mark as breaking; appends ! and a footer"),
    ] = False,
    types_csv: Annotated[
        Path | None,
        typer.Option("--types-csv", help="Optional CSV overriding the default commit type vocabulary"),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run/--no-dry-run", help="Print the message and exit without acting"),
    ] = False,
) -> None:
    config = Config.load()
    types = commit_vocab.merge_vocabularies(config.commit_type_overrides)
    if types_csv is not None:
        types = commit_vocab.merge_vocabularies((types_csv, *config.commit_type_overrides))
    _render_commit(
        commit_type,
        scope,
        description,
        body,
        breaking=breaking,
        types=types,
    )
    if dry_run:
        raise typer.Exit(0)


def _render_commit(
    commit_type: str,
    scope: str | None,
    description: str,
    body: str | None,
    *,
    breaking: bool,
    types: frozenset[str],
) -> None:
    if commit_type not in types:
        message = f"Commit type {commit_type!r} is not allowed. Allowed: {', '.join(sorted(types))}"
        typer.echo(message, err=True)
        raise typer.Exit(1)

    normalized_description = (description or "update implementation").strip().rstrip(
        "."
    ).strip() or "update implementation"
    normalized_description = normalized_description[:1].lower() + normalized_description[1:]

    scope_segment = ""
    if scope:
        if not commit_grammar.is_valid_scope(scope):
            typer.echo(f"Scope must be a single lowercase token: {scope!r}", err=True)
            raise typer.Exit(1)
        scope_segment = f"({scope})"

    exclamation = "!" if breaking else ""
    title = f"{commit_type}{scope_segment}{exclamation}: {normalized_description}"
    if len(title) > commit_grammar.title_max_length():
        typer.echo(
            f"Title exceeds {commit_grammar.title_max_length()} characters ({len(title)})",
            err=True,
        )
        raise typer.Exit(1)

    bullets: list[str] = []
    for line in strip_attribution(body, config=Config.load()):
        bullet = line if line.startswith("- ") else f"- {line.lstrip('-').strip()}"
        if len(bullet) > commit_rules.body_line_max():
            typer.echo(
                f"Body line exceeds {commit_rules.body_line_max()} characters ({len(bullet)})",
                err=True,
            )
            raise typer.Exit(1)
        bullets.append(bullet)
    body_text = "\n".join(bullets)
    rendered = (
        f"{title}\n\n{body_text}\n\nBREAKING CHANGE: {normalized_description}"
        if breaking
        else (f"{title}\n\n{body_text}" if body_text else title)
    )
    typer.echo(rendered)


@app.command("branch")
def create_branch(
    branch_type: Annotated[str, typer.Option("--type", help="Conventional branch type (e.g. feature, bugfix)")],
    description: Annotated[str, typer.Option("--description", help="Branch description in any format")],
    types_csv: Annotated[
        Path | None,
        typer.Option("--types-csv", help="Optional CSV overriding the default branch type vocabulary"),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run/--no-dry-run", help="Print the branch name and exit"),
    ] = False,
) -> None:
    _ = Config.load()
    types = branch_vocab.default_types()
    if types_csv is not None:
        types = branch_vocab.merge_vocabularies((types_csv,))
    if branch_type not in types:
        typer.echo(
            f"Branch type {branch_type!r} is not allowed. Allowed: {', '.join(sorted(types))}",
            err=True,
        )
        raise typer.Exit(1)
    name = branch_rules.build_branch_name(branch_type, branch_rules.normalize_description(description))
    typer.echo(name)
    if dry_run:
        raise typer.Exit(0)
