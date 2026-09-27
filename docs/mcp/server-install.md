---
type: playbook
title: Installing and running the MCP server
description: Requires the mcp extra, or run it on demand with uvx without installing it.
tags: [mcp]
status: stable
---

# Installing and running the MCP server

Requires the `mcp` extra: `pip install 'conventional-git[mcp]'` (the `mcp`
subcommand only registers when it's installed — see
[`architecture/optional-extras.md`](../architecture/optional-extras.md)).
Alternatively, run it on demand without installing the extra into your
environment:

```bash
uvx --from 'conventional-git[mcp]' conventional-git-mcp
```

`conventional-git mcp serve` exposes the same rules to agents over the
Model Context Protocol. The server is a thin wrapper around the spec core;
tools return the same `Violation` objects that front-ends print, in a
machine-readable shape agents can self-correct against.
