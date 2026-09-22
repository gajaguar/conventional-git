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
MUST follow [Conventional Branch](https://conventional-branch.github.io/)
(`<type>/<description>`, e.g. `feat/add-enforcement`,
`fix/normalize-description-grammar`). Both share the same `type` vocabulary
(`feat`, `fix`, `docs`, `build`, `ci`, `refactor`, `test`, `chore`, ...).

## Gate

`make check` MUST pass before any commit. Findings SHOULD be fixed with
`make fix` before editing by hand.

## Dependencies

A new tool MUST be added to the ecosystem manager that owns it
(`package.json` for Node, `pyproject.toml` `[dependency-groups].dev` for
Python, ...) and MUST only go in `mise.toml` when it bootstraps an
ecosystem or has none in this repo. A tool MUST NOT be declared in two
layers — the two pins can drift and the gate would no longer cover
both. See [`docs/toolchain.md`](docs/toolchain.md) for the full rule
and placement table.

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

## Repository metadata

The agent MUST populate the GitHub repository metadata before the first
release, and SHOULD do so in the first commit that follows instantiation of
this template:

- The repository description MUST be set to a single sentence, in English,
  without a trailing period.
- Repository topics MUST include the primary language and the project kind,
  and SHOULD include the main framework or runtime.
- The homepage URL MUST be set when the project is deployed or published,
  and MAY be left empty otherwise.
- `README.md` MUST NOT be the only place where the purpose of the project is
  stated; the description and the README first paragraph MUST agree.

The agent SHOULD apply these with `gh`:

```bash
gh repo edit --description "..." --add-topic <topic> --homepage "..."
```

The agent MUST NOT leave the description empty, and MUST NOT copy the
description of this template verbatim.

## Python

- The agent MUST NOT add docstrings to functions, methods, or classes; use a
  comment only where the *why* is not obvious from the code. The
  `pylint-plugin` `app-no-docstrings` checker enforces this and fails
  `make check`/`make pylint` otherwise.
- The agent MUST run `make check` and `make test` before committing Python
  changes, and SHOULD run `make fix` first for anything auto-fixable.
- The spec core MUST stay free of `git` imports and `SystemExit`. Returning a
  `Report` is the contract; only front-ends turn violations into exit codes.
