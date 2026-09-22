---
name: conventional-branch
description: >-
  Create git branches following the Conventional Branch specification. Use
  when the user says "create a branch", "new branch", "conventional branch",
  "start working on", "checkout a branch", or asks for branch naming help
  outside a ticket/module/team context.
argument-hint: >-
  [--ask]

  Skill flags:
    --ask    Show the drafted branch name and wait for approval before
             creating it

  Examples:
    /conventional-branch
    /conventional-branch --ask
allowed-tools: Bash, Read, AskUserQuestion
model: haiku
effort: low
context: fork
agent: Bash
---

# Conventional Branch

Draft a branch name following the
[Conventional Branch](https://conventionalbranch.org/) specification, then
delegate all validation and the branch creation itself to
`conventional-git create branch`. The CLI owns every deterministic rule (type
validity, character set, segment/separator grammar, normalization); this
skill only supplies the type and description.

## Format

```text
<type>/<description>
```

- **Type**: MUST be one entry from
  [branch-types.csv](references/branch-types.csv); MUST match the kind of
  work about to start.
- **Description**: MUST use only lowercase letters, digits, hyphens, and dots
  (dots only inside a version-like segment, e.g. `v1.2.0`); MUST NOT contain
  spaces, underscores, uppercase letters, or consecutive/leading/trailing
  hyphens or dots.
- Trunk branches (`main`, `master`, `develop`) are exempt from this format and
  MUST NOT be renamed by this skill.

## Context

- `current`: !`git branch --show-current`
- `status`: !`git status --porcelain`

## Instructions

1. MUST read [branch-types.csv](references/branch-types.csv) and choose the
   single type that matches the work about to start.
2. MUST summarize the intended work into one short, lowercase, hyphenated
   `description` (e.g. "add oauth login", not "Added OAuth Login").
3. MUST build and run the command below:

   ```bash
   conventional-git create branch \
     --type "<type>" \
     --description "<description>"
   ```

4. If and only if the arguments contain `--ask`, MUST render the branch name
   by running the command with `--dry-run`, present it with
   `AskUserQuestion`, and create it only on approval. Otherwise, MUST create
   it directly — creating without confirmation is the default behavior.
5. MUST print the result of `git switch -c <name>` (the branch name). If either
   the CLI or `git switch -c` exits non-zero, MUST fix the offending
   component and retry.

> NOTE: If `conventional-git` is not available, recommend the user install it
> with `uv tool install conventional-git` or `pipx install conventional-git`.
