---
type: decision
title: The sh privilege-drop advisory is dismissed because nothing uses _uid
description: The high-severity sh alert is dismissed as not used, and a test fails if gitlint or src starts passing sh's _uid option.
tags: [toolchain, security]
status: stable
---

# The sh privilege-drop advisory is dismissed because nothing uses `_uid`

Dependabot flags `sh` below 2.2.4 for an incomplete privilege drop: a command
started with `_uid=<user>` keeps its parent's supplementary groups. `sh` is
only here through `gitlint` (`gitlint[trusted-deps]` pins `sh==1.14.3`), so
`uv lock --upgrade-package sh` cannot move it, and neither `gitlint` nor this
project passes `_uid`.

The alert is dismissed as not used rather than worked around. A dismissal
also stops the security update PR that would arrive once `gitlint-core`
loosens its pin, so
[`tests/test_sh_uid_unused.py`](../../tests/test_sh_uid_unused.py) searches
the installed `gitlint` and `src/` for `_uid` and fails when either starts
using it. If it fails, upgrade `sh` (or switch the extra to `gitlint-core`,
which does not pin it) and reopen the alert.
