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

`adapters/gitlint_rules.py` and `adapters/commitizen_config.py` translate
between the core's `Violation` and the consumer tool's error type. They
are the only modules that import the consumer SDKs (`gitlint`, `commitizen`).

## Front-ends

- `cli/check.py` and `cli/create.py` — Typer commands. These are the only
  places that call `SystemExit`; their job is to map core output to exit
  codes and stderr text.
- `cli/hook.py` — installs and removes the Git hooks.
- `mcp/server.py` — FastMCP server exposing `validate_commit_message`,
  `validate_branch_name`, and `describe_convention`. Returns the same
  structured `Violation` shape so agents can self-correct.

`generation/` contains generation protocols and heuristics that are not yet
wired to the CLI or MCP. `helpers.py` contains shared transformations used by
the front-ends.

## Vocabulary

Vocabulary is data. `data/commit-types.csv` and `data/branch-types.csv`
are the single source of truth for what counts as a valid `type`. New
types go in the CSV, never in a regex inside the core. `data/branch-trunks.csv`
lists trunk branch names (`main`, `master`, `develop`) that are accepted
as-is, without the `<type>/` prefix.
