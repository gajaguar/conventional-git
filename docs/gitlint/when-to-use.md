---
type: guideline
title: When to reach for the gitlint extra
description: Use it when a repository already runs gitlint, or to check a whole commit range in CI.
tags: [gitlint]
status: stable
---

# When to reach for the gitlint extra

`adapters/gitlint_rules.py` hands a commit message's header and body to the
core's `validate_message()` and translates the resulting `Violation`s into
`RuleViolation`s, so a gitlint run reports the same verdict as
`conventional-git check commit`. This is an optional adapter, not a second
implementation of the rules.

- **A repository already runs gitlint.** Loading the adapter gives one
  commit linter instead of two overlapping hooks.
- **Checking a range of commits**, for example in CI with
  `gitlint --commits origin/main..HEAD`. `conventional-git check commit`
  only validates a single message; gitlint's `--commits` walks a range.

You do not need the extra on top of `conventional-git hook install` or the
`.pre-commit-hooks.yaml` hooks (see
[`enforcement/git-hooks.md`](../enforcement/git-hooks.md)). Those already
enforce the same rules per commit.
