# LLM-backed suggestions

This covers the `jev` suggestion provider (`generation/typesafe.py`) in enough
detail to decide whether to enable it: what data it sends, which credential
talks to which endpoint, how failures behave, and how to install or upgrade
the `llm` extra. See [architecture](architecture.md#front-ends) for where
this fits in the codebase.

## What leaves your machine

> **The staged diff is sent to a third party.** With the `llm` extra
> installed and a credential resolved, `create suggest` and
> `suggest_commit_message` POST the first 12,000 characters of the diff
> (`_DIFF_MAX_CHARS` in `generation/typesafe.py`), the changed file paths,
> candidate scopes and descriptions derived from them, and the configured
> commit-type vocabulary to TypeSafe's `system_one` API — either directly, or
> via OpenRouter, which forwards the request to TypeSafe. If a secret is
> staged in the diff, it is sent too.

To keep a diff local, unstage anything sensitive first, pass
`--provider heuristic`, or don't install the `llm` extra — the built-in
heuristic provider never leaves the machine. Validation (`check`, the git
hooks, CI) never calls an LLM regardless of what's installed.

## Providers and credentials

| Credential resolves                                          | Talks to          | Base URL (default)          | Model (default)     |
| ------------------------------------------------------------ | ----------------- | --------------------------- | ------------------- |
| `TYPESAFE_API_KEY`                                           | TypeSafe directly | `https://api.typesafe.ai`   | `jev-latest`        |
| `OPENROUTER_API_KEY`, or the keyring entry from `auth login` | OpenRouter        | `https://openrouter.ai/api` | `typesafe/jev-1.13` |

Credentials resolve in that order — `TYPESAFE_API_KEY` first, then
`OPENROUTER_API_KEY`, then the OS keyring (`generation/credentials.py`).

`TYPESAFE_BASE_URL` and `TYPESAFE_DEFAULT_MODEL` override the endpoint and
model on **both** paths: the TypeSafe SDK itself reads them when a
`TYPESAFE_API_KEY` is used, and `generation/typesafe.py` reads them
explicitly when building the OpenRouter client. Only the defaults above
differ between the two paths.

## Keyring scope

`conventional-git auth login` stores only an **OpenRouter** key, in the OS
keyring under service `conventional-git`, user `openrouter`. `auth logout`
clears that same entry. There is no keyring storage for a TypeSafe key — set
`TYPESAFE_API_KEY` in the environment to use it. `auth status` reports
whichever credential would actually be used (`TYPESAFE_API_KEY` first, then
the resolved OpenRouter key), not the keyring contents specifically.

Without the `llm` extra installed, the `auth` subcommands still appear in
`--help` but each one prints an install hint and exits 1.

## Failure modes

Any `ProviderError` from the `jev` provider — missing credentials, a
connection failure, an authentication or rate-limit error from the SDK — is
handled differently depending on how the provider was selected:

- **No `--provider` flag**: `create suggest` prints a one-line notice to
  stderr and falls back to the heuristic provider; the command still exits 0.
  `suggest_commit_message` (MCP) does the same and returns the fallback
  suggestion with a `"warning"` field in its response instead of raising.
- **`--provider jev` explicitly requested**: `create suggest` exits 1 with
  the error message instead of falling back.

## `--apply` does not commit

`create suggest --apply` renders the suggested commit message and validates
its type against `.conventional-git.toml` (falling back to
`data/commit-types.csv`), then prints the rendered message. It does not run
`git commit`. Pipe it into git yourself if that's what you want:

```bash
conventional-git create suggest --diff-file changes.diff --apply \
  | git commit -F -
```

## Installing the extra into an existing `uv tool` install

If `conventional-git` is already installed via `uv tool install` without the
`llm` extra, add it in place with `--force`:

```bash
# from a local checkout
uv tool install --force '.[llm]'

# from the git remote, matching the README's install command
uv tool install --force 'conventional-git[llm] @ git+https://github.com/gajaguar/conventional-git@main'
```

Without the extra, `auth` subcommands stay visible in `--help` but only print
an install hint (see [Keyring scope](#keyring-scope) above).
