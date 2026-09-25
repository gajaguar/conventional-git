from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Annotated

import typer

from conventional_git.branch import rules as branch_rules
from conventional_git.branch import vocabulary as branch_vocab
from conventional_git.commit import rules as commit_rules
from conventional_git.commit import vocabulary as commit_vocab
from conventional_git.config import Config
from conventional_git.violations import Report
from conventional_git.violations import Severity

# pylint: disable-next=app-require-final,app-module-const-naming
app = typer.Typer(help="Validate messages and branch names against the rules.")


def _report_to_exit_code(*, valid: bool) -> None:
    if not valid:
        raise typer.Exit(1)


def _print_report(target: str, report: Report) -> None:
    if report.valid and not report.warnings:
        typer.echo(f"{target}: ok")
        return
    for violation in report.violations:
        level = "warning" if violation.severity is Severity.WARNING else "error"
        typer.echo(
            f"{target}:{violation.field}: [{level}] {violation.code}: {violation.message} (fix: {violation.fix_hint})",
            err=True,
        )


@app.command("commit")
def check_commit(
    message: Annotated[
        str | None,
        typer.Option(
            "--message",
            "-m",
            help="Commit message string; reads stdin if omitted",
        ),
    ] = None,
    message_file: Annotated[
        Path | None,
        typer.Option(
            "--file",
            "-f",
            help="Path to a file containing the commit message",
        ),
    ] = None,
    types_csv: Annotated[
        Path | None,
        typer.Option(
            "--types-csv",
            help="Optional CSV overriding the default commit type vocabulary",
        ),
    ] = None,
) -> None:
    config = Config.load()
    text = _resolve_message(message, message_file)
    policy = commit_vocab.resolve_policy(config, extra_types_csv=types_csv)
    report = commit_rules.validate_message(
        text,
        allowed_types=policy.types,
        attribution_patterns=policy.extra_attribution_patterns,
    )
    _print_report("commit", report)
    _report_to_exit_code(valid=report.valid)


@app.command("branch")
def check_branch(
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="Branch name to validate; defaults to the current branch",
        ),
    ] = None,
    types_csv: Annotated[
        Path | None,
        typer.Option(
            "--types-csv",
            help="Optional CSV overriding the default branch type vocabulary",
        ),
    ] = None,
    trunks_csv: Annotated[
        Path | None,
        typer.Option(
            "--trunks-csv",
            help="Optional CSV adding to the default trunk branch names exempt from the <type>/<description> format",
        ),
    ] = None,
) -> None:
    config = Config.load()
    policy = branch_vocab.resolve_policy(config, extra_types_csv=types_csv, extra_trunks_csv=trunks_csv)
    resolved_name = name if name is not None else _current_branch()
    report = branch_rules.validate_name(resolved_name, allowed_types=policy.types, trunk_branches=policy.trunks)
    _print_report("branch", report)
    _report_to_exit_code(valid=report.valid)


def _resolve_message(message: str | None, message_file: Path | None) -> str:
    if message is not None:
        return message
    if message_file is not None:
        return message_file.read_text(encoding="utf-8")
    return sys.stdin.read()


def _current_branch() -> str:
    head_ref = os.environ.get("GITHUB_HEAD_REF")
    if head_ref:
        return head_ref
    head = Path(".git/HEAD")
    if head.exists():
        ref = head.read_text(encoding="utf-8").strip()
        if ref.startswith("ref: refs/heads/"):
            return ref[len("ref: refs/heads/") :]
    return ""
