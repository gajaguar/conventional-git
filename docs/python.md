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
avoid a second, silently divergent source of truth. `mise.toml`'s `[env]`
forces `uv` to use the mise-provided interpreter instead of downloading its
own:

```toml
[env]
UV_PYTHON_PREFERENCE = "only-system"
UV_PYTHON_DOWNLOADS = "never"
```

## Defaults we rely on

`pyproject.toml` only holds settings that change a tool's behavior. A
setting equal to the tool's default is noise: it hides the real decisions
and drifts when the default moves. These are left out on purpose:

| Omitted setting                                    | Why it is not needed                                                     |
| :------------------------------------------------- | :----------------------------------------------------------------------- |
| `license-files`                                    | hatchling picks up `LICENSE` by default                                  |
| `[tool.hatch.build.targets.wheel].packages`        | hatchling auto-detects `src/<normalized project name>`                   |
| `[tool.pytest.ini_options].testpaths`              | pytest's default recursion rules already skip `.venv` and `node_modules` |
| `[tool.coverage.run].source`                       | `addopts` passes `--cov=src`                                             |
| `exclude_lines` with `pragma: no cover`            | already a default; `exclude_also` only adds the `__main__` guard         |
| ruff `target-version`                              | inferred from `requires-python`                                          |
| ruff `lint.isort.section-order` / `case-sensitive` | ruff's defaults produce the same order                                   |
| pyright `exclude` for `.venv` / `node_modules`     | pyright excludes `**/.*` and `**/node_modules` by default                |
| extras repeated in the dev group                   | the dev group installs `conventional-git[gitlint,llm,mcp]` instead       |

Every `lint.per-file-ignores` entry must match at least one current
violation; drop it when the code that needed it goes away.
