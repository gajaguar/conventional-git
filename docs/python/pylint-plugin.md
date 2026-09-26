---
type: tool
title: The pylint-plugin dependency
description: A standalone plugin encoding personal review preferences beyond ruff's rules, installed as a uv git dependency.
tags: [python]
status: stable
---

# The pylint-plugin dependency

A standalone pylint plugin encoding personal code-review preferences beyond
ruff's rule set, installed as a `uv` git dependency tracked in
`pyproject.toml`'s `[tool.uv.sources]` — see
[the plugin's README](https://github.com/gajaguar/pylint-plugin) for the
full checker list. It's a separate repo, not vendored, so the same rules can
be reused and updated across every project built from this template without
copy-pasting checker code. The hook and `make pylint` both defer to
`pyproject.toml`'s `[tool.pylint.main].load-plugins` and
`[tool.pylint."messages control"]` — no `--enable=...`/`--load-plugins=...`
flags are duplicated on the command line, so the plugin's checker list stays
in one place.
