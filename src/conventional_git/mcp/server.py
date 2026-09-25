from __future__ import annotations

from dataclasses import asdict

from mcp.server.fastmcp import FastMCP

from conventional_git import generation
from conventional_git.branch import grammar as branch_grammar
from conventional_git.branch import rules as branch_rules
from conventional_git.branch import vocabulary as branch_vocab
from conventional_git.commit import grammar as commit_grammar
from conventional_git.commit import rules as commit_rules
from conventional_git.commit import vocabulary as commit_vocab
from conventional_git.config import Config

# pylint: disable-next=app-require-final,app-module-const-naming
mcp = FastMCP("conventional-git")


@mcp.tool()
def validate_commit_message(message: str) -> dict[str, object]:
    report = commit_rules.validate_message(message)
    return report.to_dict()


@mcp.tool()
def validate_branch_name(name: str) -> dict[str, object]:
    report = branch_rules.validate_name(name)
    return report.to_dict()


@mcp.tool()
def describe_convention() -> dict[str, object]:
    return {
        "commit": {
            "types": sorted(commit_vocab.default_types()),
            "title_max_length": commit_grammar.title_max_length(),
            "body_line_max": commit_rules.body_line_max(),
            "message_max_bytes": commit_rules.message_max_bytes(),
        },
        "branch": {
            "types": sorted(branch_vocab.default_types()),
            "trunks": sorted(branch_vocab.default_trunks()),
            "description_max_length": branch_grammar.description_max_length(),
        },
    }


@mcp.tool()
def suggest_commit_message(diff: str, changed_paths: list[str] | None = None) -> dict[str, object]:
    generation.enable_optional_providers()
    provider_name = "jev" if "jev" in generation.available_providers() else "heuristic"
    provider = generation.get_provider(provider_name)
    if provider is None:
        return {"provider": None, "suggestion": None, "error": "No suggestion provider is registered."}
    config = Config.load()
    criteria = commit_vocab.merge_criteria(config.commit_type_overrides)
    try:
        suggestion = provider.suggest(diff, changed_paths=tuple(changed_paths or ()), types=criteria)
    except generation.ProviderError as error:
        heuristic = generation.get_provider("heuristic")
        suggestion = (
            heuristic.suggest(diff, changed_paths=tuple(changed_paths or ()), types=criteria) if heuristic else None
        )
        return {
            "provider": "heuristic",
            "suggestion": asdict(suggestion) if suggestion else None,
            "warning": str(error),
        }
    return {
        "provider": provider_name,
        "suggestion": asdict(suggestion) if suggestion else None,
    }


def run() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run()
