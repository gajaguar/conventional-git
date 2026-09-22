# Conventions

## README structure

A README is written for a developer who needs to get productive. Use this
order when a section has real content:

1. **Title**, one flat-square badge row, and a short description.
2. **Why** — the background and problem the project addresses.
3. **Key features** — the capabilities a reader needs to recognize.
4. **Prerequisites** — the tools and versions required before installation.
5. **Installation** — the shortest verified installation sequence.
6. **Usage** or **Quickstart** — commands that demonstrate the main paths.
7. **CLI reference** — an enumerable command and option reference, when one
   exists.
8. **Configuration** — supported settings and their defaults, when one exists.
9. **Architecture** — design boundaries and links to deeper documentation.
10. **Open items** — known gaps or unverified assumptions, stated plainly.
11. **Contributing** — development setup, checks, and contribution rules.
12. **License** — the license and its source file.

Use **Open items** as the roadmap equivalent. Skip any section without real
content rather than padding the README to preserve the shape.

## Command convention: `check` vs `fix`

Targets are split by whether they mutate files:

| Umbrella            | Behavior                                                             |
| ------------------- | -------------------------------------------------------------------- |
| `check` (read-only) | Reports problems, exits non-zero, never writes. This is the CI gate. |
| `fix` (writable)    | Mutates files in place.                                              |

The Python targets wired into `check`/`fix` (and `install`/`test`) live in
`mk/python.mk`.

## Scoping with `FILES=`

Most targets accept `FILES="..."` to limit scope to specific paths or globs,
e.g. `make md-lint FILES="README.md"`.

## Commits and branches

Commit messages follow
[Conventional Commits](https://www.conventionalcommits.org/) and branch names
follow [Conventional Branch](https://conventional-branch.github.io/) — see
`AGENTS.md`'s "Commits and branches" section for the normative form. This
project enforces them in its own `.pre-commit-config.yaml` via the hooks
shipped in `.pre-commit-hooks.yaml`.
