---
type: playbook
title: Registering hooks with the pre-commit framework
description: Add the published .pre-commit-hooks.yaml hooks to a repository's pre-commit config and install every required hook type.
tags: [enforcement, pre-commit]
status: stable
---

# Registering hooks with the pre-commit framework

For the pre-commit framework, register both hooks with `language: system` so
the CLI is available on `PATH`:

```yaml
repos:
  - repo: https://github.com/gajaguar/conventional-git
    rev: v1.3.0
    hooks:
      - id: conventional-commit-msg
      - id: conventional-branch-name
```

Install all required hook types in the repository:

```bash
pre-commit install --hook-type commit-msg --hook-type pre-commit --hook-type pre-push
```

For an isolated environment instead of a globally installed CLI, see
[`pre-commit-local-hooks.md`](pre-commit-local-hooks.md).
