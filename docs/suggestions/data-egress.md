---
type: tool
title: What leaves your machine
description: With the llm extra and a credential, the staged diff, file paths, candidate scopes, and vocabulary are sent to TypeSafe or OpenRouter.
tags: [suggestions, llm]
status: stable
---

# What leaves your machine

This covers the `jev` suggestion provider (`generation/typesafe.py`) in
enough detail to decide whether to enable it: what data it sends, which
credential talks to which endpoint, how failures behave, and how to install
or upgrade the `llm` extra. See
[`architecture/three-layers.md`](../architecture/three-layers.md) for where
this fits in the codebase.

> **The staged diff is sent to a third party.** With the `llm` extra
> installed and a credential resolved, `create suggest` and
> `suggest_commit_message` POST the first 12,000 characters of the diff
> (`_DIFF_MAX_CHARS` in `generation/typesafe.py`), the changed file paths,
> candidate scopes and descriptions derived from them, and the configured
> commit-type vocabulary to TypeSafe's `system_one` API — either directly,
> or via OpenRouter, which forwards the request to TypeSafe. If a secret is
> staged in the diff, it is sent too.

To keep a diff local, unstage anything sensitive first, pass
`--provider heuristic`, or don't install the `llm` extra — the built-in
heuristic provider never leaves the machine. Validation (`check`, the git
hooks, CI) never calls an LLM regardless of what's installed.
