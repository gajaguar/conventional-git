---
type: rule
title: Enforcing commits and branches
description: A pre-commit hook checks the commit being written and the current branch name; make commits-check re-validates the whole range in CI, through this project's own pinned copy of itself.
tags: [git]
status: stable
---

# Enforcing commits and branches

Two layers enforce [Commits and branches](commits-and-branches.md):

* **Local**: `.pre-commit-config.yaml`'s `conventional-commit-msg` hook
  checks the message being written (`commit-msg` stage);
  `conventional-branch-name` checks the current branch name (`pre-commit`
  and `pre-push` stages). Both run through `uvx`, unconditionally.
* **CI**: `make commits-check` re-validates every commit in `$(BASE)..HEAD`
  and the branch name, since a local hook can be bypassed with
  `--no-verify`. It runs as part of `make check`.

`mk/python.mk` overrides the base Makefile's `CONVENTIONAL_GIT ?= uvx
conventional-git@latest` with `$(UV) run conventional-git`, so `make commits-check`
uses this project's own pinned dev dependency (already synced by `uv sync`)
instead of an ephemeral `uvx` fetch — faster, and reproducible from the
lockfile. `.github/workflows/{ci,python}.yml`'s checkout uses `fetch-depth:
0` and the pull request's head ref, so `$(BASE)` (`origin/main`) and the
branch name resolve correctly instead of hitting a detached `HEAD`.

Dependabot always names its branches `dependabot/<ecosystem>/<dependency>`,
which is not a Conventional Branch type, and its prefix can't be changed.
`conventional-git` therefore accepts names that start with `dependabot/` or
`renovate/` (1.1.0 and later), in the hook and in `make commits-check`
alike; the commit messages are still validated, and
`.github/dependabot.yml` sets their `ci`/`chore` prefixes.
