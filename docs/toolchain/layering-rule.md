---
type: rule
title: mise bootstraps, the ecosystem manager installs the rest
description: A tool declared in two layers can drift between them; this rule prevents that class of drift.
tags: [toolchain]
status: stable
---

# mise bootstraps, the ecosystem manager installs the rest

> **mise installs what bootstraps an ecosystem or belongs to none. The
> ecosystem's package manager installs everything else.**

A tool declared in two layers can drift between them — `make check` and the
pre-commit hook can then reach different verdicts on the same file, the
exact class of drift this rule exists to prevent. `mise.toml`'s `[env]` sets
`UV_PYTHON_PREFERENCE = "only-system"` and `UV_PYTHON_DOWNLOADS = "never"`,
which forces uv to use the mise-provided interpreter instead of shadowing it
with its own; `jdx/mise-action` exports this env in CI, and it also applies
for an end user with mise active who runs `uv tool install .`. See
[`python/interpreter-source.md`](../python/interpreter-source.md).

| Tool                                         | Where                                              | Why                                           |
| -------------------------------------------- | -------------------------------------------------- | --------------------------------------------- |
| node, pnpm, python, uv                       | `mise.toml`                                        | bootstrap: nothing else can install them      |
| checkmake                                    | `mise.toml`                                        | Go binary, no ecosystem in this repo          |
| pre-commit                                   | `mise.toml`                                        | meta-tool that runs everything else           |
| cspell, markdownlint-cli2                    | `package.json`                                     | Node dev deps, lockfile-managed               |
| ruff, mypy, pyright, pytest, pylint, gitlint | `pyproject.toml` `[dependency-groups].dev`         | Python dev deps, `uv.lock`-managed            |
| skills-ref (`agentskills`)                   | `pyproject.toml` `[dependency-groups].dev`         | Python dev dep, validates `skills/*/SKILL.md` |
| typer                                        | `pyproject.toml` `[project.dependencies]`          | Python runtime deps, `uv.lock`-managed        |
| gitlint, keyring, typesafe-sdk, mcp          | `pyproject.toml` `[project.optional-dependencies]` | Opt-in runtime extras, `uv.lock`-managed      |

See [`extras-self-reference.md`](extras-self-reference.md) for why the dev
group also pulls in the optional extras.
