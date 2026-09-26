# Contributing

Thanks for taking the time to contribute. Bug reports, documentation fixes,
and pull requests are all welcome.

## Ways to contribute

- **Report a bug or propose a feature** by opening a GitHub issue. Include
  the command you ran, what you expected, and what happened instead.
- **Fix or extend documentation** under [`docs/`](docs/index.md) — see
  "Documentation changes" below.
- **Submit a pull request** for a bug fix, a new rule, or a new front-end
  surface (CLI, MCP, adapter).

## Development setup

```bash
mise install     # pin the toolchain (Python, Node, uv, pnpm, ...)
make install      # install dependencies and git hooks
make check        # read-only validation gate
make test         # test suite
```

`make fix` applies safe auto-fixes (formatting, lint) before you fix the
rest by hand. Run `make check` and `make test` again before opening a pull
request — both MUST pass; see [`AGENTS.md`](AGENTS.md#gate).

## Commit messages and branch names

This repository dogfoods its own rules:

- Commit messages MUST follow
  [Conventional Commits](https://www.conventionalcommits.org/).
- Branch names MUST follow
  [Conventional Branch](https://conventionalbranch.org/)
  (`<type>/<description>`, e.g. `fix/normalize-branch-name`).
- Commit messages MUST NOT carry an attribution trailer (`Co-Authored-By:`,
  "Generated with …", a 🤖 marker); the project's own commit-msg hook
  rejects them — see
  [`docs/enforcement/attribution-trailers.md`](docs/enforcement/attribution-trailers.md).

The pre-commit hooks installed by `make install` enforce both automatically;
`describe_convention`/`validate_commit_message`/`validate_branch_name` are
also exposed over MCP for an agent to self-correct before committing — see
[`docs/mcp/index.md`](docs/mcp/index.md).

## Where a change belongs

The codebase is layered on purpose — see
[`AGENTS.md`](AGENTS.md#layering) and
[`docs/architecture/index.md`](docs/architecture/index.md):

1. **Spec core** (`conventional_git.commit.*`, `conventional_git.branch.*`) —
   pure validation rules, no I/O.
2. **Adapters** (`conventional_git.adapters.*`) — translate a core
   `Violation` into a consumer tool's own error type.
3. **Front-ends** (`conventional_git.cli.*`, `conventional_git.mcp.*`) — map
   user input to core calls and core output to user output.

A new rule belongs in the core, not hardcoded in an adapter. A new commit or
branch type belongs in `data/{commit,branch}-types.csv`, not a regular
expression.

## Documentation changes

`docs/` is an [OKF](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
bundle of atomic notes — one concept per file. When you add or change a
note:

- Add it to its directory's `index.md`.
- Add an entry to [`docs/log.md`](docs/log.md) describing what changed.
- Keep the note to exactly one concept; split it instead of growing it.

General documentation-writing guidance (voice, structure, frontmatter) is
kept outside this repository so it does not drift between projects that
share it — see [`docs/index.md`](docs/index.md).

## Pull requests

- Keep a pull request focused on one change; unrelated fixes belong in
  their own PR.
- Reference the issue it closes, if any.
- Expect `make check` and `make test` to run in CI; a failing gate blocks
  merge.

## License

By contributing, you agree that your contribution is licensed under this
project's [MIT License](LICENSE).
