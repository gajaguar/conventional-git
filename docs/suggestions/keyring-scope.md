---
type: reference
title: Keyring scope and auth status
description: auth login stores one key per provider in the OS keyring; auth status shows source and which one would actually be used.
tags: [suggestions, llm]
status: stable
---

# Keyring scope and auth status

`conventional-git auth login --provider typesafe|openrouter` stores one key
per provider, in the OS keyring under service `conventional-git`, user
`typesafe` or `openrouter` (default: `openrouter`, which keeps the
pre-existing entry compatible). `auth logout --provider ...` removes one
entry; `auth logout` with no flag removes both. `auth status` lists every
provider, its source (`env` or `keyring`) and which one `_build_client()`
would actually use. There is no plaintext fallback: without a usable OS
keyring backend, `auth login` fails with a message pointing at the
environment variables instead.

Without the `llm` extra installed, the `auth` subcommands still appear in
`--help` but each one prints an install hint and exits 1.
