from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from conventional_git.branch import grammar as branch_grammar
from conventional_git.branch import rules as branch_rules
from conventional_git.branch import vocabulary as branch_vocab
from conventional_git.commit import grammar as commit_grammar
from conventional_git.commit import rules as commit_rules
from conventional_git.commit import vocabulary as commit_vocab

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


def run() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run()
