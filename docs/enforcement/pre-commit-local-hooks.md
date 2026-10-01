---
type: tool
title: A repo:local pre-commit configuration
description: An isolated Python environment alternative to a globally installed CLI, pinned to a PyPI release.
tags: [enforcement, pre-commit]
status: stable
---

# A repo:local pre-commit configuration

The pre-commit framework can create an isolated Python environment without a
globally installed CLI. This local hook configuration pins the same release:

```yaml
repos:
  - repo: local
    hooks:
      - id: conventional-commit-msg
        name: conventional-git commit message
        entry: conventional-git check commit --file
        language: python
        language_version: python3.14
        additional_dependencies:
          - conventional-git==1.3.0
        stages: [commit-msg]
        pass_filenames: true
      - id: conventional-branch-name
        name: conventional-git branch name
        entry: conventional-git check branch
        language: python
        language_version: python3.14
        additional_dependencies:
          - conventional-git==1.3.0
        stages: [pre-commit, pre-push]
        always_run: true
        pass_filenames: false
```

The hook environment requires Python >=3.14. This local configuration can
drift from a separately installed global CLI, since the two are pinned
independently.
