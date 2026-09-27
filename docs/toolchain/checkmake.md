---
type: tool
title: checkmake lints the Makefile
description: A Go binary with no ecosystem in this repo, so it lives in mise.toml.
tags: [toolchain]
status: stable
---

# checkmake lints the Makefile

**checkmake** — lints the `Makefile` itself (`make makefile-lint`);
`checkmake.ini` disables the `minphony` rule's `all`/`clean` expectations,
which don't apply to this Makefile's install/check/fix/test shape.
