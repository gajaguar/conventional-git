---
type: reference
title: Defaults relied on
description: pyproject.toml only holds settings that change a tool's behavior; a setting equal to the default is omitted and recorded here instead.
tags: [python]
status: stable
---

# Defaults relied on

`pyproject.toml` only holds settings that change a tool's behavior. A
setting equal to the tool's default is noise: it hides the real decisions
and drifts when the default moves. These are left out on purpose:

| Omitted setting                                    | Why it is not needed                                                                                                                                   |
| :------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `license-files`                                    | hatchling picks up `LICENSE` by default                                                                                                                |
| `[tool.hatch.build.targets.wheel].packages`        | hatchling auto-detects `src/<normalized project name>`                                                                                                 |
| `[tool.pytest.ini_options].testpaths`              | pytest's default recursion rules already skip `.venv` and `node_modules`                                                                               |
| `[tool.coverage.run].source`                       | `addopts` passes `--cov=src`                                                                                                                           |
| `exclude_lines` with `pragma: no cover`            | already a default; `exclude_also` only adds the `__main__` guard                                                                                       |
| ruff `target-version`                              | inferred from `requires-python`                                                                                                                        |
| ruff `lint.isort.section-order` / `case-sensitive` | ruff's defaults produce the same order                                                                                                                 |
| pyright `exclude` for `.venv` / `node_modules`     | pyright excludes `**/.*` and `**/node_modules` by default                                                                                              |
| extras repeated in the dev group                   | the dev group installs `conventional-git[gitlint,llm,mcp]` instead — see [`toolchain/extras-self-reference.md`](../toolchain/extras-self-reference.md) |

Every `lint.per-file-ignores` entry must match at least one current
violation; drop it when the code that needed it goes away.
