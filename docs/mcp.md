# MCP

Requires the `mcp` extra: `pip install 'conventional-git[mcp]'` (the `mcp`
subcommand only registers when it's installed). Alternatively, run it
on demand without installing the extra into your environment:

```bash
uvx --from 'conventional-git[mcp]' conventional-git-mcp
```

`conventional-git mcp serve` exposes the same rules to agents over the
Model Context Protocol. The server is a thin wrapper around the spec core;
tools return the same `Violation` objects that front-ends print, in a
machine-readable shape agents can self-correct against.

## Plugin-bundled server

The Claude Code plugin (see [Agents](../README.md#agents)) registers this
server through the repo's `.mcp.json`, launched with
`uvx --from 'conventional-git[mcp] @ git+...@v1.0.0' conventional-git-mcp`
(the full Git URL is in `.mcp.json`). That command needs only `uv` on
`PATH` — no separate `conventional-git` install or `mcp` extra.
`conventional-git capabilities --json` reports `extras.mcp` and
`mcp_tools` so a skill can tell whether these tools are available before
recommending them.

## Tools

### `validate_commit_message(message)`

Returns a dict with `valid` and `violations[]`:

```json
{
  "valid": false,
  "violations": [
    {
      "code": "commit.description-trailing-period",
      "field": "description",
      "message": "Description must not end with a period",
      "fix_hint": "Remove the trailing period",
      "severity": "warning"
    }
  ]
}
```

### `validate_branch_name(name)`

Same shape as above.

### `describe_convention()`

Returns the live vocabulary and limits, so an agent reads the current
ruleset instead of relying on stale prompt text:

```json
{
  "commit": {
    "types": ["build", "chore", "ci", "docs", "feat", "fix", ...],
    "limits": {
      "title_max_length": 120,
      "body_line_max": 140,
      "message_max_bytes": 2048
    }
  },
  "branch": {
    "types": ["bugfix", "chore", "feature", "fix", "hotfix", "release"],
    "limits": {
      "description_max_length": 75
    }
  }
}
```

### `suggest_commit_message(diff, changed_paths=[])`

Returns a suggested `type`/`scope`/`description`/`breaking` for a diff, plus
which provider answered:

```json
{
  "provider": "jev",
  "suggestion": {
    "type": "fix",
    "scope": "cli",
    "description": "fix the login flow",
    "confidence": 0.87,
    "breaking": false
  }
}
```

This is **advice**, not a rule: `provider` is `"heuristic"` whenever the `llm`
extra isn't installed or no `TYPESAFE_API_KEY`/`OPENROUTER_API_KEY` resolves
(the call still returns a suggestion — see
[`docs/architecture.md`](architecture.md)). When `provider` is `"jev"`, the
`diff` argument was sent to TypeSafe or OpenRouter — see
[`docs/llm.md`](llm.md) for exactly what's sent. An agent should still call
`validate_commit_message` on the message it actually writes; a suggestion
passing this tool is not itself a validation result.

## Why this is the highest-value tool

Drafting a Conventional Commit from a diff is the agent's most common
failure mode. The `validate_*` tools give the agent a real feedback loop
— draft, validate, fix, commit — instead of one-shot guessing. They are
cheap, deterministic, and run before any commit actually fires.
