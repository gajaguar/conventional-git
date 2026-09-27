---
type: tool
title: pre-commit runs the shared checks
description: The git hook framework running universal hooks plus the Python and conventional-git hooks.
tags: [toolchain]
status: stable
---

# pre-commit runs the shared checks

**pre-commit** — git hook running the universal hooks (whitespace/EOF/
YAML/TOML checks, markdownlint, cspell) plus the Python and
conventional-git hooks in `.pre-commit-config.yaml`. See
[`enforcement/pre-commit-framework.md`](../enforcement/pre-commit-framework.md)
for wiring this project's own hooks into another repository.
