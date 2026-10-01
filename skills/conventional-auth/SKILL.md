---
name: conventional-auth
description: >-
  Check, set up or remove the API key behind LLM-backed commit suggestions
  with `conventional-git auth`. Use when the user says "set up the jev key",
  "login to TypeSafe", "configure OpenRouter for conventional-git", "check my
  suggestion credentials", "remove my API key", or when `create suggest` or
  `suggest_commit_message` reports missing credentials.
license: MIT
compatibility: Requires the conventional-git CLI (git, Python 3.14+, uv) with the llm extra and an OS keyring
allowed-tools: Bash Read AskUserQuestion
---

# Conventional Auth

Guide the user through the credentials the `jev` suggestion provider needs.
The CLI stores one key per provider (`typesafe`, `openrouter`) in the OS
keyring, and also reads `TYPESAFE_API_KEY` and `OPENROUTER_API_KEY` from the
environment, which win over the keyring.

## Security rules

- MUST NOT ask the user to paste an API key into the conversation.
- MUST NOT pass a key on a command line, through a pipe or heredoc, or write
  it to a file, a log or a commit.
- MUST NOT run `echo`, `printenv`, `env` or similar to reveal
  `TYPESAFE_API_KEY` or `OPENROUTER_API_KEY`, and MUST NOT read the keyring
  directly.
- `conventional-git auth status` prints only a masked key and its source, so
  its output MAY be shown to the user.

## Instructions

1. MUST run `conventional-git capabilities --json`. If it isn't available,
   follow the install NOTE below and stop. If `extras.llm` is `false`, every
   `auth` subcommand only prints an install hint and exits 1; tell the user
   to install the llm extra and stop.
2. **Check** — run `conventional-git auth status`. It lists each provider as
   `not set`, `env (<VAR>)` or `keyring`, masked, and marks the one that would
   be used with `(active)`. Resolution order: `TYPESAFE_API_KEY`,
   `OPENROUTER_API_KEY`, the `typesafe` keyring entry, the `openrouter`
   keyring entry. When a credential is already `(active)`, do nothing more.
3. **Login** — `auth login` prompts for the key with hidden input, so the
   agent MUST NOT run it. Ask which provider the user has with
   `AskUserQuestion`, then tell them to run it themselves, for example:

   ```text
   ! conventional-git auth login --provider typesafe
   ```

   `--provider` is `typesafe` or `openrouter` (default `openrouter`). If the
   OS has no usable keyring backend, `login` fails; point the user to
   exporting `TYPESAFE_API_KEY` or `OPENROUTER_API_KEY` in their own shell
   instead. Afterwards, run `conventional-git auth status` to confirm.
4. **Logout** — run `conventional-git auth logout --provider <provider>` to
   remove one entry. With no `--provider` it removes both, so MUST confirm
   with `AskUserQuestion` first. Logout never touches environment variables;
   if `auth status` still shows `env (...)`, the user has to unset the
   variable themselves.
5. Once a credential is `(active)`, the `conventional-suggest` skill can use
   the `jev` provider. Remind the user that it sends the staged diff to
   TypeSafe or OpenRouter.

> NOTE: If `conventional-git` is not available, recommend the user install it
> with `uv tool install 'conventional-git[llm]'` or
> `pipx install 'conventional-git[llm]'`. To add the extra to an existing
> install: `uv tool install --force 'conventional-git[llm]'`.
