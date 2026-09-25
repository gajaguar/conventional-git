# Toolchain

## What goes where

> **mise installs what bootstraps an ecosystem or belongs to none. The
> ecosystem's package manager installs everything else.**

A tool declared in two layers can drift between them — `make check` and
the pre-commit hook can then reach different verdicts on the same file,
the exact class of drift this rule exists to prevent. `mise.toml`'s
`[env]` sets `UV_PYTHON_PREFERENCE = "only-system"` and
`UV_PYTHON_DOWNLOADS = "never"`, which forces uv to use the mise-provided
interpreter instead of shadowing it with its own; `jdx/mise-action`
exports this env in CI, and it also applies for an end user with mise
active who runs `uv tool install .`.

| Tool                                         | Where                                              | Why                                           |
| :------------------------------------------- | :------------------------------------------------- | :-------------------------------------------- |
| node, pnpm, python, uv                       | `mise.toml`                                        | bootstrap: nothing else can install them      |
| checkmake                                    | `mise.toml`                                        | Go binary, no ecosystem in this repo          |
| pre-commit                                   | `mise.toml`                                        | meta-tool that runs everything else           |
| cspell, markdownlint-cli2                    | `package.json`                                     | Node dev deps, lockfile-managed               |
| ruff, mypy, pyright, pytest, pylint, gitlint | `pyproject.toml` `[dependency-groups].dev`         | Python dev deps, `uv.lock`-managed            |
| skills-ref (`agentskills`)                   | `pyproject.toml` `[dependency-groups].dev`         | Python dev dep, validates `skills/*/SKILL.md` |
| typer                                        | `pyproject.toml` `[project.dependencies]`          | Python runtime deps, `uv.lock`-managed        |
| gitlint, keyring, typesafe-sdk, mcp          | `pyproject.toml` `[project.optional-dependencies]` | Opt-in runtime extras, `uv.lock`-managed      |

`gitlint`, `keyring`, `typesafe-sdk`, and `mcp` are optional extras
(`gitlint`, `llm`, `mcp`), since only the adapter or front-end that imports
them needs them at runtime. The dev group pulls them in through a
self-reference, `conventional-git[gitlint,llm,mcp]`, so mypy, pyright, and
pylint can resolve them during `make check` without a second, drifting pin.

### Rejected alternatives

- **mise `npm:` / `pipx:` backends** (e.g. `"npm:cspell" = "10"`) —
  resolve at install time with no transitive lockfile, so reproducible
  installs and `--frozen-lockfile` in CI are impossible.
- **pre-commit-managed tool environments** — pre-commit fetches its own
  copies of tools that the ecosystem manager already installs, at
  independently pinned versions; the two layers can drift and reach
  different verdicts on the same file. This is why `.pre-commit-config.yaml`
  routes Python and Markdown/spell hooks through `make` targets instead of
  remote hook repos.

- **mise** — pins the high-level toolchain (`mise.toml`): Node, pnpm,
  pre-commit, and the Python runtime itself (Python, uv). Per-ecosystem
  package managers keep doing their own job (uv for Python, pnpm for Node).
- **markdownlint-cli2** + **cspell** (pnpm, dev-only) — Markdown lint and
  spell check.
- **checkmake** — lints the `Makefile` itself (`make makefile-lint`);
  `checkmake.ini` disables the `minphony` rule's `all`/`clean` expectations,
  which don't apply to this Makefile's install/check/fix/test shape.
- **pre-commit** — git hook running the universal hooks (whitespace/EOF/
  YAML/TOML checks, markdownlint, cspell) plus the Python and
  conventional-git hooks in `.pre-commit-config.yaml`.
