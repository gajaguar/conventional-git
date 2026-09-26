---
type: tool
title: Where hooks are installed
description: The installer resolves Git's configured hooks path, so it handles linked worktrees and core.hooksPath destinations like husky.
tags: [enforcement, git-hooks]
status: stable
---

# Where hooks are installed

```bash
conventional-git hook install --target ../my-repo
conventional-git hook install --target ../my-repo --force
conventional-git hook uninstall --target ../my-repo
```

Omit `--target` to use the current repository. The installer asks Git for
`rev-parse --git-path hooks`, so it handles linked worktrees and
`core.hooksPath`. In a normal repository the files land in `.git/hooks/`; in
a linked worktree they land in the shared main repository's `.git/hooks/`;
with `core.hooksPath=.husky`, they land in `.husky/`. A note is printed when
the configured path is outside the default hooks directory, because another
tool may own it.

Each generated script has a `# managed-by: conventional-git` marker.
`--force` overwrites existing hooks without a backup. `hook uninstall`
removes only hooks carrying that marker and leaves other hooks in place.

The hooks call `conventional-git` from `PATH`. Git does not version
`.git/hooks`, so each contributor installs the CLI and runs `hook install`.
