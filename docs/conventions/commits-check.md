---
type: rule
title: Enforcing commits and branches
description: A pre-commit hook checks the commit being written and the current branch name; make commits-check re-validates the whole range in CI.
tags: [git]
status: stable
---

# Enforcing commits and branches

Two layers enforce [Commits and branches](commits-and-branches.md), both via
[conventional-git](https://github.com/gajaguar/conventional-git):

* **Local**: `.pre-commit-config.yaml`'s `conventional-commit-msg` hook
  checks the message being written (`commit-msg` stage);
  `conventional-branch-name` checks the current branch name (`pre-commit`
  and `pre-push` stages).
* **CI**: `make commits-check` re-validates every commit in `$(BASE)..HEAD`
  and the branch name, since a local hook can be bypassed with
  `--no-verify`. It runs as part of `make check`.

`main` runs both through `uvx conventional-git` — an ephemeral run needing
only `uv` (pinned in `mise.toml`), not a full Python project. A language
branch MAY override the `CONVENTIONAL_GIT` Makefile variable to run its own
project-pinned copy instead — see `feat/python`'s `mk/python.mk`.
