---
type: reference
title: Three enforcement surfaces
description: The commit-msg, pre-commit, and pre-push hooks and what each one rejects.
tags: [enforcement, git-hooks]
status: stable
---

# Three enforcement surfaces

The project makes the convention unbypassable through Git hooks. A prompt
that says "MUST" is not enough; Git must run the rule.

| Surface      | When it runs                             | What it rejects                                   |
| ------------ | ---------------------------------------- | ------------------------------------------------- |
| `commit-msg` | `git commit` reads `.git/COMMIT_EDITMSG` | Non-conventional commit messages                  |
| `pre-commit` | `git commit` decides whether to proceed  | Branch name does not match `<type>/<description>` |
| `pre-push`   | `git push` decides whether to upload     | A non-conventional branch name being pushed       |

Install them with [`hook-install-path.md`](hook-install-path.md)'s
`conventional-git hook install`, or register them through the
[pre-commit framework](pre-commit-framework.md) instead.
