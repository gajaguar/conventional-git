---
type: rule
title: No docstrings
description: Comments only where the why isn't obvious; enforced by pylint-plugin's app-no-docstrings checker.
tags: [python]
status: stable
---

# No docstrings

This project does not use docstrings — use comments only where the *why*
isn't obvious from the code.
[`pylint-plugin`](https://github.com/gajaguar/pylint-plugin)'s
`app-no-docstrings` (W9001) checker fails `make check`/`make pylint` if any
function, method, or class has one. pylint has no autofix for this, so
docstrings must be removed by hand.
