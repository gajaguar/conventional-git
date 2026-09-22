---
name: conventional-commit
description: >-
  Generate and create git commits following the Conventional Commits 1.0.0
  specification. Use when the user says "commit", "conventional commit",
  "create a commit", "commit changes", or asks for commit help outside a
  gitmoji context.
argument-hint: >-
  [--ask] [--amend]

  Skill flags:
    --ask    Show the drafted message and wait for approval before committing
    --amend  Amend (reword) the last commit instead of creating a new one

  Examples:
    /conventional-commit
    /conventional-commit --ask
    /conventional-commit --amend
allowed-tools: Bash, Read, AskUserQuestion
model: haiku
effort: low
context: fork
agent: Bash
---

# Conventional Commit

Draft a commit message following the
[Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
specification, then delegate all validation and the commit itself to
`conventional-git create commit`. The CLI owns every deterministic rule
(type validity, scope format, breaking-change footer, lengths, character set,
rejection of attribution trailers such as `Co-Authored-By:`); this skill
only supplies the wording.

## Format

```text
<type>[(<scope>)][!]: <description>

- <optional body bullet>

BREAKING CHANGE: <description>   ← only when breaking
```

- **Type**: MUST be one entry from
  [commit-types.csv](references/commit-types.csv); MUST match the change
  kind.
- **Scope** (optional): a single lowercase token describing the subsystem (e.g.
  `auth`, `api`, `cli`); omit when the change is cross-cutting.
- **Breaking change**: use `--breaking` when the change is not
  backward-compatible; the CLI appends `!` to the header and emits a
  `BREAKING CHANGE:` footer automatically.
- **Description**: MUST use imperative mood and present tense; MUST start with a
  lowercase letter; MUST NOT end with a period.
- **Body** (optional): MUST be bullet points; MUST explain *why* the change was
  made or its impact, never restating *what* the diff shows; MUST keep each
  bullet on a single line.

## Context

- `status`: !`git status --porcelain`
- `diff`: !`git diff HEAD`

## Instructions

1. MUST read [commit-types.csv](references/commit-types.csv) and choose the
   single type that matches the change kind.
2. MUST summarize `diff` (and any untracked files in `status`) into one
   imperative, present-tense `description` starting with a lowercase
   letter (e.g. "add oauth login", not "Added login").
3. SHOULD draft 2–5 body bullets when the change spans multiple files or is
   sizable; otherwise you MUST leave the body empty.
4. MUST determine whether the change is breaking. If it is, pass `--breaking`.
5. MUST build and run the command below. MUST pass `--amend` if and only if the
   arguments request to amend or rewording the last commit:

   ```bash
   conventional-git create commit \
     --type "<type>" \
     --scope "<scope-or-omit-flag>" \
     --description "<description>" \
     --body "<bullets-or-empty>"
   ```

   Omit `--scope` entirely when there is no scope. The CLI does not invoke
   `git commit` itself; the skill MUST shell out to `git commit` after the
   CLI prints the rendered message, or use `git commit --amend --file=-`
   when amending.

6. If and only if the arguments contain `--ask`, MUST render the message by
   running the command with `--dry-run`, present it with `AskUserQuestion`, and
   commit only on approval. Otherwise, MUST commit directly — committing
   without confirmation is the default behavior.
7. You MUST print the result of `git commit`. If either the CLI or `git commit`
   exits non-zero, you MUST fix the offending component and retry.

> NOTE: If `conventional-git` is not available, recommend the user install it
> with `uv tool install conventional-git` or `pipx install conventional-git`.
