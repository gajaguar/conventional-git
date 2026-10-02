# AGENTS.md

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

## Agent instructions

- `AGENTS.md` is the only agent instructions file; put project rules here. The
  repository MUST NOT contain a `CLAUDE.md` or any other tool-specific copy,
  because a second copy drifts from this one; `make claude-md-check` fails on
  one.

## Command surface

- Run the `Makefile` targets (`make check`, `make fix`, `make test`, ...)
  instead of the underlying tools, so the agent and CI use the same options.
  `make help` lists them.
- Give every new target a `##` help line; `make help` prints it and
  `make help-check` fails on a target without one.

## Gate

- `make check` and `make test` MUST pass before any commit.
- Run `make fix` first for findings it can repair, then edit by hand.

## Commits and branches

- Write commit messages as
  [Conventional Commits](https://www.conventionalcommits.org/) and branch
  names as [Conventional Branch](https://conventionalbranch.org/)
  (`<type>/<description>`, e.g. `feat/add-enforcement`,
  `fix/normalize-description-grammar`). A pre-commit hook and
  `make commits-check` enforce both; see
  [`docs/conventions/commits-check.md`](docs/conventions/commits-check.md).
- Name a documentation or dependency branch `chore/...`: a branch type is not
  a commit type, and `docs/` is not one.

## Pull requests

Once a pull request is open, the agent MUST:

1. Wait for CI; while it fails, fix the cause, push to the same branch and
   wait again until it passes.
2. Squash-merge a pull request with exactly one commit and use a regular merge
   commit otherwise (`gh pr view --json commits` gives the count).
3. Delete the branch on the remote and locally.
4. Switch back to the base branch, pull it and run `git fetch --prune`.

## Documentation

- Follow the organization's shared documentation-writing guide, kept in one
  place rather than copied into this repository so it cannot drift from other
  projects that follow the same guide.
- Add a new `docs/` note to its directory's `index.md` and, by file name, to
  [`docs/log.md`](docs/log.md); `make docs-lint` fails on a missing field or a
  broken link.
- Cover exactly one concept per note.
- Write a note only when it explains something a reader cannot already get
  from `make help`, a linter's own message, or the configuration it comes
  from.

## Dependencies

- Add a new tool to the ecosystem manager that owns it (`package.json` for
  Node, `pyproject.toml` `[dependency-groups].dev` for Python); use
  `mise.toml` only for a tool that bootstraps an ecosystem or has no manager
  in this repository.
- Declare a tool in one layer only: two pins can drift and the gate would no
  longer cover both. See
  [`docs/toolchain/layering-rule.md`](docs/toolchain/layering-rule.md).

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

- Write no docstrings on functions, methods or classes; add a comment only
  where the *why* is not obvious from the code. `pylint-gajaguar`'s
  `gajaguar-no-docstrings` fails `make check` on any docstring.
- Enable the plugin with `enable = ["gajaguar"]` in `pyproject.toml`'s
  `[tool.pylint."messages control"]`, not with a list of rules, so a rule
  added by a `pylint-gajaguar` upgrade runs without a config change.
- Keep `pyproject.toml` to settings that differ from the tool's default, and
  keep a `lint.per-file-ignores` entry only while it matches a current
  violation; see
  [`docs/python/pyproject-defaults.md`](docs/python/pyproject-defaults.md).
- Keep the spec core free of `git` imports and `SystemExit`. Returning a
  `Report` is the contract; only front-ends turn violations into exit codes.
