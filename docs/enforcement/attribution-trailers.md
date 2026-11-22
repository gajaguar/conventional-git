---
type: rule
title: Attribution trailers are rejected
description: The core rejects Co-Authored-By, Generated with, and robot-emoji trailers as commit.attribution errors, extensible via config.
tags: [enforcement, commits]
status: stable
---

# Attribution trailers are rejected

The core rejects `Co-Authored-By:` trailers (human or AI), `Generated
with …` lines, and 🤖 markers as `commit.attribution` errors.
`[commit] attribution_patterns` in `.conventional-git.toml` extends the
defaults with case-insensitive regular expressions matched against each body
line. Every front-end that calls `validate_message` enforces this by
default. A repository that allows or requires such trailers sets
`[commit] disable_default_attribution_patterns = true` to skip the built-in
list; `attribution_patterns` still applies.

The same rules apply to pull request descriptions, which no Git hook sees.
`conventional-git check command` reads a shell command (or a hook JSON payload
with `tool_input.command`) from standard input. For `gh pr create|edit` and
`bitbucket pr create|update` it validates the `--title`, the `--body`, the
`--body-file` content, and any heredoc body, line by line including the first.
It exits `2` with `pr:line[N]` errors when a line matches, `0` otherwise and
for any other command; anything it cannot parse passes. Exit `2` is what a
tool-call hook needs to block the call. The plugin's `hooks/hooks.json`
registers it as a `PreToolUse` hook on `Bash`, filtered per command family so
it does not start on every call. A line that is specific to one tool, such as a
session URL, is matched per repository by adding a regular expression to
`[commit] attribution_patterns`. `check command` reads that config from the
directory the command targets (the last `cd` or `pushd` before the pull
request command, else the payload `cwd`, else the process directory),
searching upward to the repository root.
