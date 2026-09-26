---
type: tool
title: --apply renders, it does not commit
description: create suggest --apply renders and validates the suggested message but never runs git commit.
tags: [suggestions]
status: stable
---

# --apply renders, it does not commit

`create suggest --apply` renders the suggested commit message and validates
its type against `.conventional-git.toml` (falling back to
`data/commit-types.csv`), then prints the rendered message. It does not run
`git commit`. Pipe it into git yourself if that's what you want:

```bash
conventional-git create suggest --diff-file changes.diff --apply \
  | git commit -F -
```
