# MCP

`conventional-git mcp serve` exposes the same rules to agents over the
Model Context Protocol. The server is a thin wrapper around the spec core;
tools return the same `Violation` objects that front-ends print, in a
machine-readable shape agents can self-correct against.

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
    "title_max_length": 120,
    "body_line_max": 140,
    "message_max_bytes": 2048
  },
  "branch": {
    "types": ["bugfix", "chore", "feature", "fix", "hotfix", "release"],
    "description_max_length": 75
  }
}
```

## Why this is the highest-value tool

Drafting a Conventional Commit from a diff is the agent's most common
failure mode. The `validate_*` tools give the agent a real feedback loop
— draft, validate, fix, commit — instead of one-shot guessing. They are
cheap, deterministic, and run before any commit actually fires.
