---
type: reference
title: The Violation data shape
description: Violation is a frozen dataclass with code, field, message, fix_hint, and severity — the contract every layer shares.
tags: [architecture]
status: stable
---

# The Violation data shape

The spec core (see [`three-layers.md`](three-layers.md)) returns a `Report`
of `Violation`s. The shape of `Violation` is the contract every adapter and
front-end relies on:

```python
@dataclass(frozen=True, slots=True)
class Violation:
    code: str  # stable identifier (e.g. "commit.type")
    field: str  # which field is offending (e.g. "type", "body[0]")
    message: str  # human-readable explanation
    fix_hint: str  # what to change to satisfy the rule
    severity: Severity  # ERROR or WARNING
```

Every consumer — the CLI's stderr output, the gitlint adapter's
`RuleViolation`, and the MCP server's JSON response — is a projection of this
same shape, never a second source of what counts as a violation.
