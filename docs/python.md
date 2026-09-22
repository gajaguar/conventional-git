# Python layer

## Docstring policy

This project does not use docstrings — use comments only where the *why*
isn't obvious from the code.
[`pylint-plugin`](https://github.com/gajaguar/pylint-plugin)'s
`app-no-docstrings` (W9001) checker fails `make check`/`make pylint` if any
function, method, or class has one. pylint has no autofix for this, so
docstrings must be removed by hand.

## Custom pylint checkers (`pylint-plugin`)

A standalone pylint plugin encoding personal code-review preferences beyond
ruff's rule set, installed as a `uv` git dependency pinned in
`pyproject.toml`'s `[tool.uv.sources]` — see
[the plugin's README](https://github.com/gajaguar/pylint-plugin) for the
full checker list. It's a separate repo, not vendored, so the same rules can
be reused and updated across every project built from this template without
copy-pasting checker code. The hook and `make pylint` both defer to
`pyproject.toml`'s `[tool.pylint.main].load-plugins` and
`[tool.pylint."messages control"]` — no `--enable=...`/`--load-plugins=...`
flags are duplicated on the command line, so the plugin's checker list stays
in one place.

## Interpreter source

`mise.toml` is the single source for the pinned Python version;
`.python-version` is intentionally absent (mise ignores it by default) to
avoid a second, silently divergent source of truth. `pyproject.toml` forces
`uv` to use the mise-provided interpreter instead of downloading its own:

```toml
[tool.uv]
python-preference = "only-system"
python-downloads = "never"
```
