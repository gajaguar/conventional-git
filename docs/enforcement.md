# Enforcement

The project makes the convention unbypassable through Git hooks. A prompt
that says "MUST" is not enough; Git must run the rule.

## Three enforcement surfaces

| Surface       | When it runs                                | What it rejects                                          |
| ------------- | ------------------------------------------- | -------------------------------------------------------- |
| `commit-msg`  | `git commit` reads `.git/COMMIT_EDITMSG`    | Non-conventional commit messages                         |
| `pre-commit`  | `git commit` decides whether to proceed     | Branch name does not match `<type>/<description>`        |
| `pre-push`    | `git push` decides whether to upload        | A non-conventional branch name being pushed              |

The hooks are installed by:

```bash
conventional-git hook install
```

The installer asks Git for `rev-parse --git-path hooks`, so it handles linked
worktrees and `core.hooksPath`. In a normal repository the files land in
`.git/hooks/`; in a linked worktree they land in the shared main repository's
`.git/hooks/`; with `core.hooksPath=.husky`, they land in `.husky/`. A note is
printed when the configured path is outside the default hooks directory because
another tool may own it.

Each generated script has a `# managed-by: conventional-git` marker. Use
`--force` to overwrite existing hooks; it makes no backup. `hook uninstall`
removes only marked hooks and skips other files. The hooks call
`conventional-git` from `PATH`, and Git does not version `.git/hooks`, so each
contributor installs the CLI and runs `hook install`.

## pre-commit integration

The project also ships `.pre-commit-hooks.yaml` so any repo can register both
checks via the `pre-commit` framework:

```yaml
repos:
  - repo: https://github.com/gajaguar/conventional-git
    rev: v0.1.0
    hooks:
      - id: conventional-commit-msg
      - id: conventional-branch-name
```

Install every required hook type:

```bash
pre-commit install --hook-type commit-msg --hook-type pre-commit --hook-type pre-push
```

The `commit-msg` hook accepts `--file <path>` where pre-commit passes
`.git/COMMIT_EDITMSG`. The published hooks use `language: system`, so
`conventional-git` must be on `PATH`. A `repo: local` configuration can use
`language: python` and `additional_dependencies: [git+https://github.com/gajaguar/conventional-git@v0.1.0]`
to create an isolated environment without a global CLI. Set
`language_version: python3.14`; the hook environment requires Python >=3.14.
The local environment can drift from a separately installed global CLI.

## CI recipe

Local hooks can be bypassed with `--no-verify`, so CI should repeat the checks:

```bash
conventional-git check branch -n "$BRANCH_NAME"
git log --format=%B -n1 | conventional-git check commit
```

With the `gitlint` extra installed, check the whole range of commits a pull
request introduces in one pass — something `check commit` can't do on its
own — instead of looping over individual messages; see
[`docs/gitlint.md`](gitlint.md):

```bash
gitlint --commits origin/main..HEAD
```

## Division of labour

- **All rules** live in the core (`commit.rules.validate_message` and
  `branch.rules.validate_name`) — the spec baseline (type, scope, header
  shape) and the house rules (imperative mood, lowercase head, no trailing
  period, bullet bodies, ≤140 char body lines, ≤2048 byte messages) alike.
  There is no split between a spec-checking tool and a house-rules tool;
  every front-end and adapter calls the same functions.
- **Front-ends** (CLI, hooks, MCP) call the core directly and turn its
  `Report` into an exit code or a structured response.
- **The gitlint adapter** (`adapters/gitlint_rules.py`) is an optional
  translation layer, not a second rule set: it hands the message to the core
  and reformats the `Violation` objects as `RuleViolation`s, so its verdict
  matches `conventional-git check commit`. See [`docs/gitlint.md`](gitlint.md)
  for when to use it.
- **The commitizen adapter** (`adapters/commitizen_config.py`) is a library
  function, `commitizen_config.emit_json()`, that emits a `cz_customize`
  `schema_pattern` built from `data/commit-types.csv` for `cz check` /
  `cz bump` to consume. It checks only the header's type/scope shape — none
  of the other house rules — and nothing in this project wires it into the
  CLI or the hooks; a repository that wants it writes the emitted block into
  its own `.cz.toml`.
- **Attribution trailers** — the core rejects `Co-Authored-By:` trailers
  (human or AI), `Generated with …` lines and 🤖 markers as
  `commit.attribution` errors; `[commit] attribution_patterns` in
  `.conventional-git.toml` extends the defaults with case-insensitive regular
  expressions matched against each body line. Every front-end that calls
  `validate_message` enforces this by default.
- **Branch names** — ours alone. Neither gitlint nor commitizen validates
  branch names; this is the genuine gap and the project's differentiator.

## Single-source vocabulary

`data/{commit,branch}-types.csv` is read by the core (default vocabulary),
by `commitizen_config.py` (which emits a `cz customize` `schema_pattern`
from the same file), and by the SKILL.md files (so an agent's vocabulary
read from the prompt matches what the validator enforces).
