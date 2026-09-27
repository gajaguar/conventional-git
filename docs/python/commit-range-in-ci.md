---
type: rule
title: Using the project's own conventional-git in CI
description: mk/python.mk overrides CONVENTIONAL_GIT to run the pinned dev dependency instead of the base Makefile's ephemeral uvx fetch.
tags: [python, ci]
status: stable
---

# Using the project's own conventional-git in CI

`make commits-check` and its enforcement are defined once, in the base
Makefile and `.pre-commit-config.yaml` — see
[`docs/conventions/commits-check.md`](../conventions/commits-check.md).
`mk/python.mk` only overrides the `CONVENTIONAL_GIT` variable:

```make
CONVENTIONAL_GIT := $(UV) run conventional-git
```

This runs the project's own pinned
[`conventional-git`](https://github.com/gajaguar/conventional-git) dev
dependency (already synced by `uv sync`) instead of the base default's
ephemeral `uvx conventional-git` fetch — faster, and reproducible from the
lockfile.

The pre-commit hooks (`conventional-commit-msg`, `conventional-branch-name`)
still run through `uvx`, unconditionally; only `make commits-check`'s CI
re-check uses the project-pinned copy. `.github/workflows/python.yml`'s
checkout uses `fetch-depth: 0` and
`ref: ${{ github.event.pull_request.head.sha || github.ref }}`, so `$(BASE)`
(`origin/main`) and the branch name resolve correctly instead of hitting a
detached `HEAD`.
