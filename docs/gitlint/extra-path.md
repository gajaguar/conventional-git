---
type: playbook
title: Locating extra-path
description: gitlint's extra-path needs a filesystem path to gitlint_rules.py, not an import name.
tags: [gitlint]
status: stable
---

# Locating extra-path

gitlint's `extra-path` needs a filesystem path to `gitlint_rules.py`, not an
import name. Ask the interpreter that has the package installed:

```bash
"$(uv tool dir)/conventional-git/bin/python" \
  -c 'import conventional_git.adapters.gitlint_rules as m; print(m.__file__)'
```

The path is inside the tool's private environment and changes on reinstall
or upgrade, so re-run this after either.
