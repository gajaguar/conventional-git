---
type: decision
title: The dev group self-references its own extras
description: So mypy, pyright, and pylint resolve gitlint/llm/mcp during make check without a second, drifting pin.
tags: [toolchain]
status: stable
---

# The dev group self-references its own extras

`gitlint`, `keyring`, `typesafe-sdk`, and `mcp` are optional extras
(`gitlint`, `llm`, `mcp`), since only the adapter or front-end that imports
them needs them at runtime. The dev group pulls them in through a
self-reference, `conventional-git[gitlint,llm,mcp]`, so mypy, pyright, and
pylint can resolve them during `make check` without a second, drifting pin.
