---
type: playbook
title: CI recipe
description: The commands CI should run to re-check commits and branch names, since local hooks can be bypassed with --no-verify.
tags: [enforcement, ci]
status: stable
---

# CI recipe

Local hooks can be bypassed with `--no-verify`, so CI should repeat the
checks:

```bash
conventional-git check branch -n "$BRANCH_NAME"
git log --format=%B -n1 | conventional-git check commit
```

With the `gitlint` extra installed, check the whole range of commits a pull
request introduces in one pass — something `check commit` can't do on its
own — instead of looping over individual messages; see
[`gitlint/wiring.md`](../gitlint/wiring.md):

```bash
gitlint --commits origin/main..HEAD
```
