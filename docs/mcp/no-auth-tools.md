---
type: decision
title: Why credential management is not an MCP tool
description: A login tool would send the raw API key through the protocol and the client's context before it reached the keyring, so auth stays CLI-only.
tags: [mcp, suggestions, llm]
status: stable
---

# Why credential management is not an MCP tool

`auth login`, `auth status` and `auth logout` are CLI-only. A `login` MCP
tool would need the raw API key as an argument, so the key would travel
through the protocol and the client's context (the model's transcript, client
logs, any provider-side retention) before reaching the OS keyring. The CLI
reads it with hidden terminal input, so it never enters an agent's context;
the `conventional-auth` skill follows the same rule and tells the user to run
`auth login` themselves.

`status` and `logout` stay out as well, so the MCP surface is the
deterministic core plus one advisory suggestion tool; see
[`architecture/validation-vs-generation.md`](../architecture/validation-vs-generation.md).
To set the credential, see
[`out-of-band-auth.md`](out-of-band-auth.md).
