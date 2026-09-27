---
type: rule
title: Attribution trailers are rejected
description: The core rejects Co-Authored-By, Generated with, and robot-emoji trailers as commit.attribution errors, extensible via config.
tags: [enforcement, commits]
status: stable
---

# Attribution trailers are rejected

The core rejects `Co-Authored-By:` trailers (human or AI), `Generated
with …` lines, and 🤖 markers as `commit.attribution` errors.
`[commit] attribution_patterns` in `.conventional-git.toml` extends the
defaults with case-insensitive regular expressions matched against each body
line. Every front-end that calls `validate_message` enforces this by
default; the default patterns cannot currently be disabled — see the
README's Open items.
