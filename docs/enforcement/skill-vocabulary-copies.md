---
type: rule
title: Skill vocabulary copies stay byte-identical
description: SKILL.md files ship their own CSV copy because a distributed skill cannot read the installed package's data/ directory.
tags: [enforcement, agents]
status: stable
---

# Skill vocabulary copies stay byte-identical

`data/{commit,branch}-types.csv` is read by the core (default vocabulary)
and by `commitizen_config.py` (which emits a `cz customize` `schema_pattern`
from the same file — see
[`commitizen-adapter.md`](commitizen-adapter.md)). The `SKILL.md` files ship
their own copy under `skills/*/references/`, because a distributed skill
cannot read the installed package's `data/` directory;
`tests/test_skill_vocabularies.py` keeps that copy byte-identical to
`data/`, and `make test` fails if it drifts. See
[`architecture/vocabulary-as-data.md`](../architecture/vocabulary-as-data.md).
