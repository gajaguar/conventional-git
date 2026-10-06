---
name: conventional-suggest
description: >-
  Suggest a Conventional Commits message from the staged diff with
  `conventional-git create suggest`. Use when the user says "suggest a commit
  message", "what should this commit be", "draft a commit from the diff",
  "use jev for the commit", or wants an LLM-backed draft instead of writing
  the message by hand.
license: MIT
compatibility: Requires the conventional-git CLI (git, Python 3.14+, uv); the jev provider also needs the llm extra and a credential
allowed-tools: Bash Read AskUserQuestion
---

# Conventional Suggest

Seed a commit message from the staged diff with
`conventional-git create suggest`, then hand it to the `conventional-commit`
skill to refine and commit. A suggestion is advice, not a validation result:
`conventional-git create commit` still validates the message you actually
write.

## Providers

- `jev` — LLM-backed (TypeSafe, or OpenRouter). Used by default when
  `capabilities` lists it in `providers`. **Sends the staged diff to a third
  party.**
- `heuristic` — built in, never leaves the machine. Used when `jev` is
  unavailable, or when `--provider heuristic` is passed.

Without `--provider`, a `jev` failure (missing credentials, connection,
rate limit) prints a notice on stderr and falls back to `heuristic` with exit
0. With `--provider jev` the same failure exits 1.

## When to use it

- Prefer it for a large or unfamiliar diff, or when the user asks for it.
- Draft by hand (`conventional-commit`) for a tiny change, or when the staged
  diff holds anything sensitive.

## Context

- `status`: !`git status --porcelain`
- `staged`: !`git diff --cached --stat`

If `status`/`staged` above are empty or still show the literal `` !`...` ``
text (the agent doesn't support this injection), run
`git status --porcelain` and `git diff --cached --stat` yourself before
continuing.

## Instructions

1. MUST run `conventional-git capabilities --json` first. If it isn't
   available, follow the install NOTE below and stop. Read `extras.llm`,
   `providers` and `credentials`.
2. If nothing is staged, MUST stop and tell the user to stage changes; the
   CLI exits 1 with "No staged changes".
3. Decide the provider:
   - `jev` is in `providers` with a non-null `credentials` entry: MUST warn
     once that the first 12,000 characters of the staged diff, the changed
     paths and the commit-type vocabulary will be sent to TypeSafe or
     OpenRouter, and MUST ask the user to approve with `AskUserQuestion`. On
     refusal, use `--provider heuristic`.
   - Otherwise the heuristic provider answers; no approval is needed.
4. MUST run:

   ```bash
   conventional-git create suggest [--provider heuristic]
   ```

   It reads `git diff --cached`. For a diff saved to a file, pass
   `--diff-file <path>`, or `--diff-file -` to read it from stdin.
5. Read `type`, `scope`, `description`, `breaking` and `confidence`. If stderr
   reports a fallback because credentials are missing, offer the
   `conventional-auth` skill.
6. Hand the result to the `conventional-commit` skill: keep the `type` and
   `breaking` unless the diff contradicts them, rewrite `description` to
   imperative mood, and add a body when the change warrants one. A low
   `confidence` is a reason to read the diff yourself before accepting it.
7. As a shortcut when the suggestion needs no edits, MAY run
   `conventional-git create suggest --apply | git commit --file=-`.
   `--apply` only renders and validates the message; it never commits.

> NOTE: If `conventional-git` is not available, recommend the user install it
> with `uv tool install conventional-git` or `pipx install conventional-git`.
> The `jev` provider needs the llm extra:
> `uv tool install --force 'conventional-git[llm]'`.
