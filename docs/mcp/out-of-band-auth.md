---
type: playbook
title: Authenticate the MCP server through the CLI
description: The MCP server has no login, logout or status tools; set the key with conventional-git auth login before the server starts, and launch it with the llm extra.
tags: [mcp, suggestions, llm]
status: stable
---

# Authenticate the MCP server through the CLI

The MCP server exposes no `login`, `logout` or `status` tool. For
`suggest_commit_message` to use the `jev` provider, set the credential
out-of-band, before the client starts the server:

1. Run `conventional-git auth login --provider typesafe|openrouter` in a
   terminal. It prompts for the key with hidden input and stores it in the OS
   keyring.
2. Run `conventional-git auth status` to confirm which credential is active.
3. Launch the server with both extras, so `jev` can register:

   ```bash
   uvx --from 'conventional-git[mcp,llm]' conventional-git-mcp
   ```

The server reads the same keyring entry as the CLI (per OS user), and also
`TYPESAFE_API_KEY` or `OPENROUTER_API_KEY` from the environment the client
launches it with; see
[`suggestions/providers-and-credentials.md`](../suggestions/providers-and-credentials.md)
and [`suggestions/keyring-scope.md`](../suggestions/keyring-scope.md).
Prefer the keyring: putting the key in the client's MCP `env` block writes
the secret to a config file.

The Claude Code plugin's bundled server does not install the `llm` extra, so
it always answers with the heuristic provider, whatever `auth login` stored;
see [`plugin-bundled-server.md`](plugin-bundled-server.md). Without a
credential, or without the extra, `suggest_commit_message` still returns a
suggestion; see [`suggest-commit-message.md`](suggest-commit-message.md). The
reason there is no MCP auth tool is in
[`no-auth-tools.md`](no-auth-tools.md).
