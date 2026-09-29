# AGENTS.md

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

## Command surface

The agent MUST use the `Makefile` targets (`make check`, `make fix`,
`make test`, ...) instead of invoking the underlying tools directly, and
MUST NOT add a target without its `##` help line.

## Commits and branches

Commit messages MUST follow
[Conventional Commits](https://www.conventionalcommits.org/); branch names
MUST follow [Conventional Branch](https://conventionalbranch.org/)
(`<type>/<description>`, e.g. `feat/add-enforcement`,
`fix/normalize-description-grammar`). Both share the same `type` vocabulary
(`feat`, `fix`, `docs`, `build`, `ci`, `refactor`, `test`, `chore`, ...). A
pre-commit hook and `make commits-check` enforce both — see
[`docs/conventions/commits-check.md`](docs/conventions/commits-check.md).

## Gate

`make check` MUST pass before any commit. Findings SHOULD be fixed with
`make fix` before editing by hand.

## Documentation

Documentation MUST follow the organization's shared documentation-writing
guide, kept in one place rather than copied into this repository so it
cannot drift from other projects that follow the same guide. A new `docs/`
note MUST be added to its directory's `index.md` and to
[`docs/log.md`](docs/log.md). A note MUST cover exactly one concept.

## Dependencies

A new tool MUST be added to the ecosystem manager that owns it
(`package.json` for Node, `pyproject.toml` `[dependency-groups].dev` for
Python, ...) and MUST only go in `mise.toml` when it bootstraps an
ecosystem or has none in this repo. A tool MUST NOT be declared in two
layers — the two pins can drift and the gate would no longer cover
both. See [`docs/toolchain/layering-rule.md`](docs/toolchain/layering-rule.md)
for the full rule and placement table.

## Layering

The codebase is intentionally three layers; the agent MUST NOT cross the
boundaries below.

1. **Spec core** — `conventional_git.commit.*` and `conventional_git.branch.*`.
   Pure functions, no git calls, no `SystemExit`, no I/O. Validation returns
   a `Report` of `Violation`s. This is the only layer that holds rules.
2. **Adapters** — `conventional_git.adapters.*` (gitlint rules, commitizen
   schema emitter). Translate `Violation` into the consumer tool's error
   type. The adapter is the only place that imports the consumer SDK.
3. **Front-ends** — `conventional_git.cli.*` and `conventional_git.mcp.*`.
   Map user input into core calls and core output into user output. These
   are the only layers that may call `SystemExit`.

A new rule MUST land in the core; an adapter that hardcodes the rule
duplicates it. A new vocabulary entry MUST land in
`data/{commit,branch}-types.csv`; a regex inside the core is a bug, not a
feature.

## Python

- The agent MUST NOT add docstrings to functions, methods, or classes; use a
  comment only where the *why* is not obvious from the code. The
  `pylint-gajaguar` `gajaguar-no-docstrings` checker enforces this and fails
  `make check`/`make pylint` otherwise.
- The agent MUST run `make check` and `make test` before committing Python
  changes, and SHOULD run `make fix` first for anything auto-fixable.
- The agent MUST NOT add a `pyproject.toml` setting that equals the tool's
  default, and every `lint.per-file-ignores` entry MUST match a current
  violation — see
  [`docs/python/pyproject-defaults.md`](docs/python/pyproject-defaults.md).
- The spec core MUST stay free of `git` imports and `SystemExit`. Returning a
  `Report` is the contract; only front-ends turn violations into exit codes.
