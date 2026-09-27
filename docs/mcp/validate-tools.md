---
type: reference
title: validate_commit_message and validate_branch_name
description: Both return the same valid/violations[] shape as the core's Violation objects.
tags: [mcp]
status: stable
---

# validate_commit_message and validate_branch_name

`validate_commit_message(message)` returns a dict with `valid` and
`violations[]`:

```json
{
  "valid": false,
  "violations": [
    {
      "code": "commit.description-trailing-period",
      "field": "description",
      "message": "Description must not end with a period",
      "fix_hint": "Remove the trailing period",
      "severity": "warning"
    }
  ]
}
```

`validate_branch_name(name)` returns the same shape. See
[`architecture/violation-contract.md`](../architecture/violation-contract.md)
for the underlying `Violation` dataclass this mirrors.
