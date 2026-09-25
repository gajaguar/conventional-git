# The gitlint extra

`adapters/gitlint_rules.py` hands a commit message's header and body to the
core's `validate_message()` and translates the resulting `Violation`s into
`RuleViolation`s, so a gitlint run reports the same verdict as
`conventional-git check commit`. This is an optional adapter, not a second
implementation of the rules.

## When to use it

- **A repository already runs gitlint.** Loading the adapter gives one commit
  linter instead of two overlapping hooks.
- **Checking a range of commits**, for example in CI with
  `gitlint --commits origin/main..HEAD`. `conventional-git check commit` only
  validates a single message; gitlint's `--commits` walks a range.

You do not need the extra on top of `conventional-git hook install` or the
`.pre-commit-hooks.yaml` hooks (see [`docs/enforcement.md`](enforcement.md)).
Those already enforce the same rules per commit.

## Install

The rule file imports the `conventional_git` package, so `gitlint` and
`conventional-git` must resolve from the same Python environment. Installing
the `gitlint` extra alongside the package does that:

```bash
REPO=https://github.com/gajaguar/conventional-git
uv tool install "conventional-git[gitlint] @ git+$REPO@main" \
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

## Locating `extra-path`

gitlint's `extra-path` needs a filesystem path to `gitlint_rules.py`, not an
import name. Ask the interpreter that has the package installed:

```bash
"$(uv tool dir)/conventional-git/bin/python" \
  -c 'import conventional_git.adapters.gitlint_rules as m; print(m.__file__)'
```

The path is inside the tool's private environment and changes on reinstall
or upgrade, so re-run this after either.

## Recommended `.gitlint`

```ini
[general]
extra-path = /path/from/the/command/above/gitlint_rules.py
ignore = B1,B5,B6,T1,T3,T5
```

Without `ignore`, gitlint's own built-in rules still run alongside the
adapter and can reject a message the core accepts — for example, `B6`
("body message is missing") flags any single-line header even though the
core allows it. The ignored built-ins are exported as
`gitlint_rules.RECOMMENDED_IGNORE` so the list here can't drift from the
code:

| Rule             | Why it's ignored                                                                           |
| ---------------- | ------------------------------------------------------------------------------------------ |
| `B1`             | 80-char body line limit; the core's limit is 140.                                          |
| `B5`             | Requires a body on every commit; the core doesn't.                                         |
| `B6`             | Requires a body; a single-line conventional commit is valid.                               |
| `T1`, `T3`, `T5` | Title length/case/punctuation checks that overlap or conflict with the core's header rule. |

Add `[CG1]` with `warnings = true` to also report the core's warnings (which
don't fail `conventional-git check commit`) as gitlint violations:

```ini
[CG1]
warnings=true
```

## Behavior versus the CLI

- Same verdict: warnings are dropped unless `[CG1] warnings = true` is set,
  matching the CLI's default exit code.
- `.conventional-git.toml` (`type_overrides`, `attribution_patterns`) is
  resolved from the commit's repository root and honored the same way the
  CLI honors it.
- Every finding surfaces as gitlint rule `CG1`, with the underlying core
  violation code embedded in the message
  (`conventional-git/<code> ERROR: <field>: <message>`).
- gitlint has no concept of branch names; it only ever sees commit messages.
  `conventional-git check branch` or the `pre-commit`/`pre-push` hooks are
  still the only branch-name enforcement.

## Wiring it up

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
