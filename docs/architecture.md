# Architecture

Three layers are deliberately separated. A new rule MUST land in the core; an
adapter that hardcodes the rule duplicates it.

```text
┌─ spec core ─────────────────────────────────────────────┐
│ pure functions, no git, no I/O                          │
│ parse + validate → list[Violation(code, field, message, │
│                                   fix_hint)]            │
└─────────────────────────────────────────────────────────┘
        ↑                    ↑                    ↑
┌───────┴────────┐  ┌────────┴───────┐  ┌─────────┴──────┐
│ enforcement    │  │ MCP server     │  │ CLI            │
│ commit-msg /   │  │ validate_* +   │  │ create + check │
│ pre-push hooks │  │ describe_*     │  │ (human path)   │
│ gitlint rules  │  │                │  │                │
│ cz check       │  │                │  │                │
└────────────────┘  └────────────────┘  └────────────────┘
```

## Spec core

`commit/rules.py` and `branch/rules.py` are the only files that hold the
rule definitions. They take primitive input (a string, an optional
vocabulary set) and return a `Report` of `Violation`s. They MUST NOT import
anything that performs git operations or raises `SystemExit`. The shape of
the `Violation` data is the contract:

```python
@dataclass(frozen=True, slots=True)
class Violation:
    code: str  # stable identifier (e.g. "commit.type")
    field: str  # which field is offending (e.g. "type", "body[0]")
    message: str  # human-readable explanation
    fix_hint: str  # what to change to satisfy the rule
    severity: Severity  # ERROR or WARNING
```

## Adapters

`adapters/gitlint_rules.py` translates between the core's `Violation` and
gitlint's error type; it is the only module that imports the gitlint SDK.
See [`docs/gitlint.md`](gitlint.md) for when and how to use it.
`adapters/commitizen_config.py` emits a commitizen `pyproject.toml`/`.cz.toml`
block as plain data (dict/JSON) — commitizen itself reads that config, so the
adapter has no SDK to import.

## Front-ends

- `cli/check.py` and `cli/create.py` — Typer commands. These are the only
  places that call `SystemExit`; their job is to map core output to exit
  codes and stderr text.
- `cli/hook.py` — installs and removes the Git hooks.
- `cli/auth.py` — stores/reads the OpenRouter credential used by the `jev`
  suggestion provider (requires the `llm` extra).
- `mcp/server.py` — FastMCP server exposing `validate_commit_message`,
  `validate_branch_name`, `describe_convention`, and `suggest_commit_message`.
  The `validate_*`/`describe_*` tools return the same structured `Violation`
  shape so agents can self-correct; `suggest_commit_message` returns advice,
  not a rule, and its output still has to pass `validate_commit_message`.
  Requires the `mcp` extra; `cli/app.py` only registers the `mcp` subcommand
  when it's importable, so a plain install doesn't pull in the MCP SDK's
  dependency tree.

`generation/` holds the `SuggestionProvider` protocol (`protocol.py`), a
regex-based `HeuristicProvider` (`heuristic.py`) that is always available,
and an optional `JevProvider` (`typesafe.py`) backed by TypeSafe's Jev model.
Both `create suggest` (CLI) and `suggest_commit_message` (MCP) call
`get_provider` the same way, so a suggestion provider is opt-in in **both**
front-ends, not tied to one of them:

- **Validation stays deterministic everywhere.** `check`, the git hooks, and
  CI never call an LLM — see `commit/rules.py` and `branch/rules.py`.
- **Suggestion is opt-in.** `JevProvider` only registers when the `llm` extra
  (`typesafe-sdk`, `keyring`) is installed, and only answers when a
  `TYPESAFE_API_KEY` or `OPENROUTER_API_KEY` resolves (see
  `generation/credentials.py`). Without either, `create suggest` and
  `suggest_commit_message` fall back to `HeuristicProvider` and print a
  notice; they never fail the command.
- This follows validation-vs-generation, not CLI-vs-MCP: MCP sampling (the
  spec mechanism that would let a server borrow the client's model) was
  deprecated upstream (SEP-2577, 2026-07-28) and Claude Code, Codex, and
  Cursor never implemented it, so an MCP tool needs its own API key exactly
  like the CLI does.

`helpers.py` contains shared transformations used by the front-ends.

## Vocabulary

Vocabulary is data. `data/commit-types.csv` and `data/branch-types.csv`
are the single source of truth for what counts as a valid `type`. New
types go in the CSV, never in a regex inside the core. `data/branch-trunks.csv`
lists trunk branch names (`main`, `master`, `develop`) that are accepted
as-is, without the `<type>/` prefix.
