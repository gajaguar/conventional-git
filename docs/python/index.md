# Python layer

Decisions specific to this project's Python implementation.

* [No docstrings](docstring-policy.md) - comments only where the *why*
  isn't obvious.
* [The pylint-plugin dependency](pylint-plugin.md) - personal review
  preferences beyond ruff's rule set.
* [Interpreter source](interpreter-source.md) - `mise.toml` as the single
  source for the pinned Python version.
* [Defaults relied on](pyproject-defaults.md) - settings intentionally left
  out because they equal a tool's default.
