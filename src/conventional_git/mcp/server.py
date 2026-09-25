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
    policy = commit_vocab.resolve_policy(Config.load())
    report = commit_rules.validate_message(
        message,
        allowed_types=policy.types,
        attribution_patterns=policy.extra_attribution_patterns,
    )
    return report.to_dict()


@mcp.tool()
def validate_branch_name(name: str) -> dict[str, object]:
    policy = branch_vocab.resolve_policy(Config.load())
    report = branch_rules.validate_name(name, allowed_types=policy.types, trunk_branches=policy.trunks)
    return report.to_dict()


@mcp.tool()
def describe_convention() -> dict[str, object]:
    config = Config.load()
    commit_policy = commit_vocab.resolve_policy(config)
    branch_policy = branch_vocab.resolve_policy(config)
    return {
        "commit": {
            "types": sorted(commit_policy.types),
            "title_max_length": commit_grammar.title_max_length(),
            "body_line_max": commit_rules.body_line_max(),
            "message_max_bytes": commit_rules.message_max_bytes(),
        },
        "branch": {
            "types": sorted(branch_policy.types),
            "trunks": sorted(branch_policy.trunks),
            "description_max_length": branch_grammar.description_max_length(),
        },
    }


@mcp.tool()
def suggest_commit_message(diff: str, changed_paths: list[str] | None = None) -> dict[str, object]:
    config = Config.load()
    criteria = commit_vocab.merge_criteria(config.commit_type_overrides)
    result = generation.suggest(diff, changed_paths=tuple(changed_paths or ()), types=criteria)
    if result.error is not None:
        return {"provider": None, "suggestion": None, "error": result.error}
    payload: dict[str, object] = {
        "provider": result.provider,
        "suggestion": asdict(result.suggestion) if result.suggestion else None,
    }
    if result.warning is not None:
        payload["warning"] = result.warning
    return payload


def run() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run()
