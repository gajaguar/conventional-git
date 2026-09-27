---
type: reference
title: Providers and credential resolution order
description: Which credential talks to which endpoint and model, and the exact resolution order.
tags: [suggestions, llm]
status: stable
---

# Providers and credential resolution order

| Credential resolves                                                       | Talks to          | Base URL (default)          | Model (default)     |
| ------------------------------------------------------------------------- | ----------------- | --------------------------- | ------------------- |
| `TYPESAFE_API_KEY`, or the `typesafe` keyring entry from `auth login`     | TypeSafe directly | `https://api.typesafe.ai`   | `jev-latest`        |
| `OPENROUTER_API_KEY`, or the `openrouter` keyring entry from `auth login` | OpenRouter        | `https://openrouter.ai/api` | `typesafe/jev-1.13` |

Credentials resolve in that order — `TYPESAFE_API_KEY`, then
`OPENROUTER_API_KEY`, then the `typesafe` keyring entry, then the
`openrouter` keyring entry (`generation/credentials.py`).

`TYPESAFE_BASE_URL` and `TYPESAFE_DEFAULT_MODEL` override the endpoint and
model on **both** paths: the TypeSafe SDK itself reads them when a
`TYPESAFE_API_KEY` is used, and `generation/typesafe.py` reads them
explicitly when building the OpenRouter client. Only the defaults above
differ between the two paths.

Never print a resolved credential's value to a terminal, log, or commit —
`auth status` (see [`keyring-scope.md`](keyring-scope.md)) reports only its
masked form and source for this reason.
