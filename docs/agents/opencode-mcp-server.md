---
type: playbook
title: opencode MCP server
description: Configure opencode to load the conventional-git MCP server via uvx, with copy-ready config snippets.
tags: [agents, opencode, mcp]
status: stable
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

## Global config: `~/.config/opencode/opencode.json`

```json
{
  "$schema": "https://opencode.ai/config.json",
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
is an argument array — executable first, then each argument. Add
`"enabled": true` to make the intent explicit.[^opencode-mcp]

## Project config: `opencode.json`

A project-scoped alternative — useful when only one checkout needs the
server. Put the same `mcp` block in `opencode.json` at the project root.
Config files are merged and the project file overrides the global one on
conflicting keys; see
[`opencode-mcp-config.md`](opencode-mcp-config.md) for the full
precedence list.

## Verifying

```bash
opencode mcp list
```

Lists every configured MCP server and its authentication status. The
agent can then call `validate_commit_message`,
`validate_branch_name`, `describe_convention`, and
`suggest_commit_message` the same way it does in Claude Code.[^opencode-mcp]

[^opencode-mcp]: opencode MCP servers
