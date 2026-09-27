---
type: guideline
title: Recommended .gitlint config
description: extra-path plus an ignore list of built-in gitlint rules that conflict with the core's own rules.
tags: [gitlint]
status: stable
---

# Recommended .gitlint config

```ini
[general]
extra-path = /path/from/the/command/above/gitlint_rules.py
ignore = B1,B5,B6,T1,T3,T5
```

Without `ignore`, gitlint's own built-in rules still run alongside the
adapter and can reject a message the core accepts — for example, `B6`
("body message is missing") flags any single-line header even though the
core allows it. The ignored built-ins are exported as
`gitlint_rules.RECOMMENDED_IGNORE` so the list here can't drift from the
code:

| Rule             | Why it's ignored                                                                           |
| ---------------- | ------------------------------------------------------------------------------------------ |
| `B1`             | 80-char body line limit; the core's limit is 140.                                          |
| `B5`             | Requires a body on every commit; the core doesn't.                                         |
| `B6`             | Requires a body; a single-line conventional commit is valid.                               |
| `T1`, `T3`, `T5` | Title length/case/punctuation checks that overlap or conflict with the core's header rule. |

Add `[CG1]` with `warnings = true` to also report the core's warnings (which
don't fail `conventional-git check commit`) as gitlint violations:

```ini
[CG1]
warnings=true
```
