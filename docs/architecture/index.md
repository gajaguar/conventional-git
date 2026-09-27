# Architecture

The three-layer design — spec core, adapters, front-ends — and the
decisions that follow from it.

* [Three layers, deliberately separated](three-layers.md) - the spec core,
  adapters, and front-ends, and what each may import.
* [The Violation data shape](violation-contract.md) - the frozen dataclass
  every layer shares.
* [Vocabulary is data](vocabulary-as-data.md) - commit and branch types live
  in CSV, never in a regex.
* [Validation versus generation](validation-vs-generation.md) - a
  suggestion provider is opt-in in both the CLI and MCP.
* [Optional extras stay lazily imported](optional-extras.md) - the `mcp`
  subcommand only registers when its SDK is installed.
