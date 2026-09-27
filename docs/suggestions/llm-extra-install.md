---
type: playbook
title: Installing the llm extra afterward
description: Add the llm extra to an existing uv tool install without reinstalling from scratch.
tags: [suggestions, llm]
status: stable
---

# Installing the llm extra afterward

If `conventional-git` is already installed via `uv tool install` without the
`llm` extra, add it in place with `--force`:

```bash
# from a local checkout
uv tool install --force '.[llm]'

# from PyPI, matching the README's install command
uv tool install --force 'conventional-git[llm]'
```

Without the extra, `auth` subcommands stay visible in `--help` but only
print an install hint (see [`keyring-scope.md`](keyring-scope.md)).
