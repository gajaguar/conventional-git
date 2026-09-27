---
type: reference
title: describe_convention returns the live vocabulary
description: So an agent reads the current ruleset instead of relying on stale prompt text.
tags: [mcp]
status: stable
---

# describe_convention returns the live vocabulary

```json
{
  "commit": {
    "types": ["build", "chore", "ci", "docs", "feat", "fix", ...],
    "limits": {
      "title_max_length": 120,
      "body_line_max": 140,
      "message_max_bytes": 2048
    }
  },
  "branch": {
    "types": ["bugfix", "chore", "feature", "fix", "hotfix", "release"],
    "limits": {
      "description_max_length": 75
    }
  }
}
```
