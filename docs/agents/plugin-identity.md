---
type: reference
title: Plugin identity
description: The marketplace, plugin, and skill names for this project, plus the prerequisites and copy-ready install commands.
resource: https://github.com/gajaguar/conventional-git
tags: [agents]
status: stable
sources:
  - id: claude-discover-plugins
    resource: https://code.claude.com/docs/en/discover-plugins
    title: Discover and install Claude Code plugins
    author: team:anthropic
---

# Plugin identity

This project ships as a Claude Code plugin, an Agent Skills directory,
and a bundled MCP server.[^claude-discover-plugins] The marketplace,
plugin, and skill names below match this repository's own
`.claude-plugin/` and `skills/` directories.

## Names

| Asset                | Name                                                                                       |
| :------------------- | :----------------------------------------------------------------------------------------- |
| Marketplace          | `conventional-git-skills`                                                                  |
| Plugin               | `conventional-git`                                                                         |
| MCP server           | `conventional-git`                                                                         |

## Skills

| Skill                  | Trigger phrasing                                                                                                                       |
| :--------------------- | :------------------------------------------------------------------------------------------------------------------------------------- |
| `conventional-commit`  | `commit`, `conventional commit`, `create a commit`, `commit changes` (outside a gitmoji context)                                       |
| `conventional-branch`  | `create a branch`, `new branch`, `conventional branch`, `start working on`, `checkout a branch` (outside a ticket/module/team context) |
| `conventional-suggest` | `suggest a commit message`, `what should this commit be`, `draft a commit from the diff`, `use jev for the commit`                     |
| `conventional-auth`    | `set up the jev key`, `login to TypeSafe`, `configure OpenRouter`, `check my suggestion credentials`, `remove my API key`              |

## Prerequisites

- Install the CLI the skills delegate to: `uv tool install conventional-git`.
- `uvx` on `PATH` (ships with `uv`) — required for the MCP server, both
  bundled in the plugin and loaded standalone from opencode.

## Install

Claude Code:

```text
/plugin marketplace add gajaguar/conventional-git
/plugin install conventional-git@conventional-git-skills
/reload-plugins
```

Any other Agent Skills-compatible agent:

```bash
npx skills add gajaguar/conventional-git
```

opencode:

```bash
npx skills add gajaguar/conventional-git -a opencode -y
```

## Examples

See [`install-channels.md`](install-channels.md) for what each channel
delivers, and the rest of `docs/agents/` for scopes, management, and
the opencode MCP setup.

[^claude-discover-plugins]: Discover and install Claude Code plugins
