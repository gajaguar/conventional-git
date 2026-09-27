---
type: playbook
title: Wiring gitlint into a repo
description: Register gitlint's own hook, or add a repo:local pre-commit entry, and check a whole commit range in CI.
tags: [gitlint]
status: stable
---

# Wiring gitlint into a repo

Register gitlint's own hook:

```bash
gitlint install-hook
```

Or, in a `pre-commit` config that already uses `repo: local` for other
tools:

```yaml
- repo: local
  hooks:
    - id: gitlint
      name: gitlint
      entry: gitlint
      language: system
      stages: [commit-msg]
```

In CI, check the whole range of commits a pull request introduces:

```bash
gitlint --commits origin/main..HEAD
```
