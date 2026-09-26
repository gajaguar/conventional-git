---
type: convention
title: Where the house rules live
description: All rules, spec baseline and house rules alike, live in the core; there is no separate spec-checking tool.
tags: [enforcement, architecture]
status: stable
---

# Where the house rules live

**All rules** live in the core (`commit.rules.validate_message` and
`branch.rules.validate_name`) — the spec baseline (type, scope, header
shape) and the house rules (imperative mood, lowercase head, no trailing
period, bullet bodies, ≤140 char body lines, ≤2048 byte messages) alike.
There is no split between a spec-checking tool and a house-rules tool;
every front-end and adapter calls the same functions.

- **Front-ends** (CLI, hooks, MCP) call the core directly and turn its
  `Report` into an exit code or a structured response.
- **The gitlint adapter** (`adapters/gitlint_rules.py`) is an optional
  translation layer, not a second rule set: it hands the message to the core
  and reformats the `Violation` objects as `RuleViolation`s, so its verdict
  matches `conventional-git check commit`. See
  [`gitlint/behavior-vs-cli.md`](../gitlint/behavior-vs-cli.md).
- **The commitizen adapter** — see
  [`commitizen-adapter.md`](commitizen-adapter.md).
- **Branch names** — see [`branch-name-gap.md`](branch-name-gap.md).

See [`architecture/three-layers.md`](../architecture/three-layers.md) for the
layering this follows from.
