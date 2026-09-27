---
type: decision
title: "Failure modes: fallback versus hard failure"
description: Without an explicit --provider jev flag, any ProviderError falls back to the heuristic provider instead of failing the command.
tags: [suggestions, llm]
status: stable
---

# Failure modes: fallback versus hard failure

Any `ProviderError` from the `jev` provider — missing credentials, a
connection failure, an authentication or rate-limit error from the SDK — is
handled differently depending on how the provider was selected:

- **No `--provider` flag**: `create suggest` prints a one-line notice to
  stderr and falls back to the heuristic provider; the command still exits
  0. `suggest_commit_message` (MCP) does the same and returns the fallback
  suggestion with a `"warning"` field in its response instead of raising.
- **`--provider jev` explicitly requested**: `create suggest` exits 1 with
  the error message instead of falling back.

This follows validation-vs-generation, not CLI-vs-MCP — see
[`architecture/three-layers.md`](../architecture/three-layers.md).
