---
type: tool
title: Behavior versus the CLI
description: Same verdict as the CLI, honors .conventional-git.toml the same way, and has no concept of branch names.
tags: [gitlint]
status: stable
---

# Behavior versus the CLI

- Same verdict: warnings are dropped unless `[CG1] warnings = true` is set,
  matching the CLI's default exit code.
- `.conventional-git.toml` (`type_overrides`, `attribution_patterns`) is
  resolved from the commit's repository root and honored the same way the
  CLI honors it.
- Every finding surfaces as gitlint rule `CG1`, with the underlying core
  violation code embedded in the message
  (`conventional-git/<code> ERROR: <field>: <message>`).
- gitlint has no concept of branch names; it only ever sees commit messages.
  [`conventions/commits-and-branches.md`](../conventions/commits-and-branches.md)
  or the `pre-commit`/`pre-push` hooks are still the only branch-name
  enforcement — see
  [`enforcement/branch-name-gap.md`](../enforcement/branch-name-gap.md).
