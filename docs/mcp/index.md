# MCP

The Model Context Protocol server: a thin wrapper exposing the spec core to
agents.

* [Installing and running the MCP server](server-install.md) - the `mcp`
  extra, or `uvx` on demand.
* [The Claude Code plugin's bundled server](plugin-bundled-server.md) -
  launched via `uvx`, needing only `uv` on `PATH`.
* [validate_commit_message and validate_branch_name](validate-tools.md) -
  the shared `valid`/`violations[]` response shape.
* [describe_convention returns the live vocabulary](describe-convention.md) -
  types and limits, read live instead of hardcoded in a prompt.
* [suggest_commit_message is advice, not a rule](suggest-commit-message.md) -
  still requires a `validate_commit_message` pass.
* [Why validate_* is the highest-value tool](self-correction-loop.md) - a
  real draft/validate/fix loop instead of one-shot guessing.
