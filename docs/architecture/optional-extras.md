---
type: decision
title: Optional extras stay lazily imported
description: cli/app.py only registers the mcp subcommand when it's importable, so a plain install doesn't pull in the MCP SDK's dependency tree.
tags: [architecture]
status: stable
---

# Optional extras stay lazily imported

`mcp/server.py` — `MCPServer` exposing `validate_commit_message`,
`validate_branch_name`, `describe_convention`, and `suggest_commit_message`.
The `validate_*`/`describe_*` tools return the same structured `Violation`
shape so agents can self-correct; `suggest_commit_message` returns advice,
not a rule, and its output still has to pass `validate_commit_message`.
Requires the `mcp` extra; `cli/app.py` only registers the `mcp` subcommand
when it's importable, so a plain install doesn't pull in the MCP SDK's
dependency tree.

The same pattern applies to the `gitlint` and `llm` extras: each adapter or
provider is only imported by the one module that needs it, and
`conventional-git capabilities --json` reports which extras, providers, and
credential sources are actually available, so a skill or agent can check
before recommending a command that needs one.
