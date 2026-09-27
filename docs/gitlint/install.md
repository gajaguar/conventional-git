---
type: playbook
title: Installing the gitlint extra
description: gitlint and conventional-git must resolve from the same Python environment.
tags: [gitlint]
status: stable
---

# Installing the gitlint extra

The rule file imports the `conventional_git` package, so `gitlint` and
`conventional-git` must resolve from the same Python environment. Installing
the `gitlint` extra alongside the package does that:

```bash
uv tool install "conventional-git[gitlint]" \
  --with-executables-from gitlint-core
```

`uv tool install` only exposes the main package's own entry points by
default, so `--with-executables-from gitlint-core` is what puts `gitlint` on
`PATH` alongside `conventional-git`. Without it, `gitlint` stays inside the
tool's private virtual environment and isn't runnable directly. If you
already installed `conventional-git` as a tool without the extra, reinstall
with `--reinstall` to add it.

A `uv pip install '.[gitlint]'` into a project virtualenv also works and
needs no extra flag, since every console script in that environment lands on
its `bin/`.
