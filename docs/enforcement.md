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
conventional-kit hook install
```

which writes three files into `<repo>/.git/hooks/` of the target repo.

## pre-commit integration

The project also ships `.pre-commit-hooks.yaml` so any repo can register
the same checks via the `pre-commit` framework:

```yaml
repos:
  - repo: https://github.com/gajaguar/conventional-kit
    rev: v0.1.0
    hooks:
      - id: conventional-commit-msg
```

The `commit-msg` hook accepts `--file <path>` where pre-commit passes
`.git/COMMIT_EDITMSG`. It uses `language: system`, so `conventional-kit`
must be on `PATH`. The branch hook currently passes no value to `--name` and
is listed as an open item in the README.

## Division of labour

- **Conventional Commits spec baseline** — `commitizen` (`cz check
  --commit-msg-file`). Actively maintained; `cz bump` and changelog
  generation come free later.
- **House rules** (imperative mood, lowercase head, no trailing period,
  bullet bodies, ≤140 char body lines, ≤2048 byte messages) — `gitlint`
  user rules via `extra-path`. Its `CommitRule` / `LineRule` API is
  exactly this shape, and the rules are pure translations of
  `Violation` objects.
- **Attribution trailers** — the core rejects `Co-Authored-By:` trailers
  (human or AI), `Generated with …` lines and 🤖 markers as
  `commit.attribution` errors; `[commit] attribution_patterns` in
  `.conventional-kit.toml` adds more. Every front-end that calls
  `validate_message` enforces this by default.
- **Branch names** — ours alone. Neither tool validates branch names;
  this is the genuine gap and the project's differentiator.

## Single-source vocabulary

`data/{commit,branch}-types.csv` is read by the core (default vocabulary),
by `commitizen_config.py` (which emits a `cz customize` `schema_pattern`
from the same file), and by the SKILL.md files (so an agent's vocabulary
read from the prompt matches what the validator enforces).
