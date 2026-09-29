---
type: rule
title: Vocabulary is data
description: Commit and branch type vocabularies live in CSV files, never in a regex inside the spec core.
tags: [architecture]
status: stable
---

# Vocabulary is data

`data/commit-types.csv` and `data/branch-types.csv` are the single source of
truth for what counts as a valid `type`. New types go in the CSV, never in a
regex inside the core. `data/branch-trunks.csv` lists trunk branch names
(`main`, `master`, `develop`) that are accepted as-is, without the
`<type>/` prefix, and `data/branch-exempt-prefixes.csv` lists name prefixes
(`dependabot/`, `renovate/`) accepted the same way, because the bot that
creates the branch picks its name.

See [`enforcement/skill-vocabulary-copies.md`](../enforcement/skill-vocabulary-copies.md)
for how the distributed `skills/*/` copies stay in sync with these files.
