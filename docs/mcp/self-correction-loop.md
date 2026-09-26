---
type: decision
title: Why validate_* is the highest-value tool
description: Drafting a Conventional Commit from a diff is the agent's most common failure mode; a real feedback loop beats one-shot guessing.
tags: [mcp, agents]
status: stable
---

# Why validate_* is the highest-value tool

Drafting a Conventional Commit from a diff is the agent's most common
failure mode. The `validate_*` tools (see
[`validate-tools.md`](validate-tools.md)) give the agent a real feedback
loop — draft, validate, fix, commit — instead of one-shot guessing. They are
cheap, deterministic, and run before any commit actually fires.
