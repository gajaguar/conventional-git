---
name: conventional-commit
description: >-
  Generate and create git commits following the Conventional Commits 1.0.0
  specification. Use when the user says "commit", "conventional commit",
  "create a commit", "commit changes", or asks for commit help outside a
  gitmoji context.
license: MIT
compatibility: Requires the conventional-git CLI (git, Python 3.14+, uv)
allowed-tools: Bash Read AskUserQuestion
---

# Conventional Commit

Draft a commit message following the
[Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
specification, then delegate all validation and the commit itself to
`conventional-git create commit`. The CLI owns every deterministic rule
(type validity, scope format, breaking-change footer, lengths, character set,
rejection of attribution trailers such as `Co-Authored-By:`); this skill
only supplies the wording.

## Arguments

- `--ask` — show the drafted message and wait for approval before committing.
- `--amend` — amend (reword) the last commit instead of creating a new one.
- `--suggest` — opt into seeding the draft from `conventional-git create
  suggest` (see step 2 below). Sends the staged diff to a third-party
  provider when one is configured; never used unless passed.

Examples: `/conventional-commit`, `/conventional-commit --ask`,
`/conventional-commit --amend`, `/conventional-commit --suggest`.

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

If `status`/`diff` above are empty or still show the literal `` !`...` ``
text (the agent doesn't support this injection), run
`git status --porcelain` and `git diff HEAD` yourself before continuing.

## Instructions

1. MUST run `conventional-git capabilities --json` first. If it isn't
   available, follow the install NOTE below and stop. Otherwise:
   - Note `version`; if it differs from this plugin's version, warn the user
     once that the CLI and skill may be out of sync.
   - If `extras.mcp` is `true`, mention that `validate_commit_message`,
     `validate_branch_name`, `describe_convention`, and
     `suggest_commit_message` are also available as MCP tools.
2. MUST read [commit-types.csv](references/commit-types.csv) and choose the
   single type that matches the change kind.
3. If and only if `--suggest` was passed, AND capabilities reports `jev` in
   `providers` with a non-null `credentials.typesafe` or
   `credentials.openrouter`, MAY seed a draft with
   `git diff --cached | conventional-git create suggest --diff-file -`
   before refining it in the next step. Skip this step entirely — including
   the `create suggest` call — when `--suggest` was not passed; the diff
   MUST NOT leave the machine without that explicit opt-in.
4. MUST summarize `diff` (and any untracked files in `status`), refining any
   seed from step 3, into one imperative, present-tense `description`
   starting with a lowercase letter (e.g. "add oauth login", not "Added
   login").
5. SHOULD draft 2–5 body bullets when the change spans multiple files or is
   sizable; otherwise you MUST leave the body empty.
6. MUST determine whether the change is breaking. If it is, pass `--breaking`.
7. MUST build and run the command below. `--amend` is a skill flag only; the
   CLI has no `--amend` option and MUST NOT be passed one:

   ```bash
   conventional-git create commit \
     --type "<type>" \
     --scope "<scope-or-omit-flag>" \
     --description "<description>" \
     --body "<bullets-or-empty>"
   ```

   Omit `--scope` entirely when there is no scope. The CLI never invokes
   `git commit` itself, whether or not `--dry-run` is passed — it only prints
   the rendered message; the skill MUST always shell out to `git commit`
   itself: `git commit --amend --file=-` if and only if the arguments request
   amending or rewording the last commit, otherwise `git commit --file=-`.

8. If and only if the arguments contain `--ask`, MUST render the message by
   running the command with `--dry-run` (an alias for the default printing
   behavior kept for forward compatibility, in case the command later gains
   side effects), present it with `AskUserQuestion`, and commit only on
   approval. Otherwise, MUST commit directly — committing without
   confirmation is the default behavior.
9. You MUST print the result of `git commit`. If either the CLI or `git commit`
   exits non-zero, you MUST fix the offending component and retry.

> NOTE: If `conventional-git` is not available, recommend the user install it
> with `uv tool install 'git+https://github.com/gajaguar/conventional-git@v1.0.0'`
> or `pipx install 'git+https://github.com/gajaguar/conventional-git@v1.0.0'`
> (the package is not published on PyPI).
