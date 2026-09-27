---
type: tool
title: The commitizen adapter is opt-in
description: commitizen_config.emit_json() emits a cz_customize schema_pattern from the CSV vocabulary; nothing wires it in by default.
tags: [enforcement, adapters]
status: stable
---

# The commitizen adapter is opt-in

`adapters/commitizen_config.py` is a library function,
`commitizen_config.emit_json()`, that emits a `cz_customize`
`schema_pattern` built from `data/commit-types.csv` for `cz check` /
`cz bump` to consume. It checks only the header's type/scope shape — none of
the other house rules (see [`house-rules.md`](house-rules.md)) — and nothing
in this project wires it into the CLI or the hooks; a repository that wants
it writes the emitted block into its own `.cz.toml`.
