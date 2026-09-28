---
type: tool
title: The Claude Code plugin's bundled server
description: The plugin's .mcp.json launches the server via uvx tracking the latest PyPI release, needing only uv on PATH.
tags: [mcp, agents]
status: stable
---

# The Claude Code plugin's bundled server

The Claude Code plugin registers this server through the repo's
`.mcp.json`, launched with
`uvx --from 'conventional-git[mcp]@latest' conventional-git-mcp` (the exact
spec is in `.mcp.json`). That command needs only `uv` on `PATH` — no
separate `conventional-git` install or `mcp` extra.
`conventional-git capabilities --json` reports `extras.mcp` and
`mcp_tools` so a skill can tell whether these tools are available before
recommending them.
