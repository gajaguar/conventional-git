---
type: decision
title: Interpreter source
description: mise.toml is the single source for the pinned Python version; uv is forced to use the mise-provided interpreter instead of downloading its own.
tags: [python]
status: stable
---

# Interpreter source

`mise.toml` is the single source for the pinned Python version;
`.python-version` is intentionally absent (mise ignores it by default) to
avoid a second, silently divergent source of truth. `mise.toml`'s `[env]`
forces `uv` to use the mise-provided interpreter instead of downloading its
own:

```toml
[env]
UV_PYTHON_PREFERENCE = "only-system"
UV_PYTHON_DOWNLOADS = "never"
```

See [`toolchain/layering-rule.md`](../toolchain/layering-rule.md) for why
this matters beyond a single machine.
