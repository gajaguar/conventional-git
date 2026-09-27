---
type: decision
title: Rejected install backends
description: "mise's npm:/pipx: backends and pre-commit-managed tool environments were both rejected in favor of ecosystem package managers."
tags: [toolchain]
status: stable
---

# Rejected install backends

- **mise `npm:` / `pipx:` backends** (e.g. `"npm:cspell" = "10"`) —
  resolve at install time with no transitive lockfile, so reproducible
  installs and `--frozen-lockfile` in CI are impossible.
- **pre-commit-managed tool environments** — pre-commit fetches its own
  copies of tools that the ecosystem manager already installs, at
  independently pinned versions; the two layers can drift and reach
  different verdicts on the same file. This is why `.pre-commit-config.yaml`
  routes Python and Markdown/spell hooks through `make` targets instead of
  remote hook repos.
