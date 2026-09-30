---
type: playbook
title: opencode MCP server
description: Configure opencode to load the conventional-git MCP server via uvx, with copy-ready config snippets.
tags: [agents, opencode, mcp]
status: stable
generated: { by: claude-code/claude-opus-5-5, at: 2026-09-29T00:00:00Z }
sources:
  - id: opencode-mcp
    resource: https://opencode.ai/docs/mcp-servers/
    title: opencode MCP servers
    author: team:sst-opencode
---

# opencode MCP server

Wire the `conventional-git` MCP server into opencode by adding it under
the `mcp` key in opencode's own config file. The server is launched on
demand with `uvx`, so `uv` must be on `PATH`; no separate
`conventional-git` install or `mcp` extra is required.[^opencode-mcp]

The bundled server uses the same command and arguments as this
repository's `.mcp.json` (see
[`../mcp/plugin-bundled-server.md`](../mcp/plugin-bundled-server.md)).

## `~/.config/opencode/config.json`

```json
{
  "mcp": {
    "conventional-git": {
      "type": "local",
      "command": [
        "uvx",
        "--from",
        "conventional-git[mcp]@latest",
        "conventional-git-mcp"
      ]
    }
  }
}
```

`type` is `"local"` (a process the opencode runtime spawns); `command`
is an argument array — executable first, then each argument. Leave
`enabled` out (defaults to `true`) or set it explicitly to `true` to
load the server on every opencode start.[^opencode-mcp]

## `.opencode/config.json`

A project-scoped alternative — useful when only one checkout needs the
server. Drop the same block into `.opencode/config.json` at the
project root, or into a top-level `opencode.json`. Path precedence
favors local config over the global one (see
[`../mcp/index.md`](../mcp/index.md)).

## Verifying

```bash
opencode mcp list
```

Lists every configured server, its type, its command, and whether it is
enabled. The agent can then call `validate_commit_message`,
`validate_branch_name`, `describe_convention`, and
`suggest_commit_message` the same way it does in Claude Code.[^opencode-mcp]

[^opencode-mcp]: opencode MCP servers
