---
type: decision
title: Validation versus generation
description: A suggestion provider is opt-in in both the CLI and MCP, not tied to one of them, and never replaces deterministic validation.
tags: [architecture, suggestions]
status: stable
---

# Validation versus generation

`generation/` holds the `SuggestionProvider` protocol (`protocol.py`), a
regex-based `HeuristicProvider` (`heuristic.py`) that is always available,
and an optional `JevProvider` (`typesafe.py`) backed by TypeSafe's Jev model.
Both `create suggest` (CLI) and `suggest_commit_message` (MCP) call
`get_provider` the same way, so a suggestion provider is opt-in in **both**
front-ends, not tied to one of them:

- **Validation stays deterministic everywhere.** `check`, the git hooks, and
  CI never call an LLM — see `commit/rules.py` and `branch/rules.py`.
- **Suggestion is opt-in.** `JevProvider` only registers when the `llm`
  extra (`typesafe-sdk`, `keyring`) is installed, and only answers when a
  credential resolves (see
  [`suggestions/providers-and-credentials.md`](../suggestions/providers-and-credentials.md)).
  Failure behavior is in
  [`suggestions/provider-fallback.md`](../suggestions/provider-fallback.md).
- This follows validation-vs-generation, not CLI-vs-MCP: MCP sampling (the
  spec mechanism that would let a server borrow the client's model) was
  deprecated upstream (SEP-2577, 2026-07-28) and Claude Code, Codex, and
  Cursor never implemented it, so an MCP tool needs its own API key exactly
  like the CLI does.

See [`suggestions/data-egress.md`](../suggestions/data-egress.md) for what
data this sends and to whom.
