---
type: guideline
title: suggest_commit_message is advice, not a rule
description: Returns a suggested type/scope/description/breaking plus which provider answered; still needs validate_commit_message afterward.
tags: [mcp, suggestions]
status: stable
---

# suggest_commit_message is advice, not a rule

`suggest_commit_message(diff, changed_paths=[])` returns a suggested
`type`/`scope`/`description`/`breaking` for a diff, plus which provider
answered:

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

`provider` is `"heuristic"` whenever the `llm` extra isn't installed or no
`TYPESAFE_API_KEY`/`OPENROUTER_API_KEY` resolves (the call still returns a
suggestion — see
[`architecture/validation-vs-generation.md`](../architecture/validation-vs-generation.md)).
When `provider` is `"jev"`, the `diff` argument was sent to TypeSafe or
OpenRouter — see
[`suggestions/data-egress.md`](../suggestions/data-egress.md) for exactly
what's sent. An agent should still call `validate_commit_message` on the
message it actually writes; a suggestion passing this tool is not itself a
validation result.

## Missing credentials

The tool never requests `jev` explicitly, so a missing credential falls back
to the heuristic and reports why in `warning`; it does not raise and does not
set `error`:

```json
{
  "provider": "heuristic",
  "suggestion": {
    "type": "fix",
    "scope": null,
    "description": "...",
    "confidence": 0.4,
    "breaking": false
  },
  "warning": "No TypeSafe or OpenRouter API key found. ..."
}
```

Without the `llm` extra, `jev` never registers: the response is the same
heuristic suggestion with no `warning`. The `error` field (with `provider`
and `suggestion` set to `null`) appears only for an unknown provider, which
this tool cannot request. The MCP server cannot set the credential; see
[`out-of-band-auth.md`](out-of-band-auth.md) and
[`no-auth-tools.md`](no-auth-tools.md), and
[`suggestions/provider-fallback.md`](../suggestions/provider-fallback.md) for
the other failure modes.
