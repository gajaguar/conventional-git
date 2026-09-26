---
type: decision
title: Branch names are this project's differentiator
description: Neither gitlint nor commitizen validates branch names; this project does, and enforces it through its own hooks.
tags: [enforcement, branches]
status: stable
---

# Branch names are this project's differentiator

**Branch names** — ours alone. Neither gitlint nor commitizen validates
branch names; this is the genuine gap and the project's differentiator. See
[`git-hooks.md`](git-hooks.md) for the `pre-commit`/`pre-push` surfaces that
enforce it, and [`gitlint/behavior-vs-cli.md`](../gitlint/behavior-vs-cli.md)
for confirmation that gitlint has no concept of branch names at all.
