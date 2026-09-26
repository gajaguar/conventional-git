---
type: rule
title: Commits and branches follow published specs
description: Commit messages follow Conventional Commits and branch names follow Conventional Branch, enforced via this project's own hooks.
tags: [conventions]
status: stable
---

# Commits and branches follow published specs

Commit messages follow
[Conventional Commits](https://www.conventionalcommits.org/) and branch
names follow [Conventional Branch](https://conventionalbranch.org/) —
see `AGENTS.md`'s "Commits and branches" section for the normative form.
This project enforces them in its own `.pre-commit-config.yaml` via the
hooks shipped in `.pre-commit-hooks.yaml` — see
[`enforcement/pre-commit-framework.md`](../enforcement/pre-commit-framework.md).
