---
okf_version: "0.2"
---

# Documentation

This is an [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
(OKF) bundle: one Markdown concept per file, each with YAML frontmatter, laid
out under this directory. Generic guidance on how to write this kind of
bundle and its README (OKF conventions, atomic notes, voice and tone,
section order) is kept in one place, outside this repository, instead of
copied here where it would drift from other projects that follow it.

## Reference

* [Architecture](architecture/index.md) - the spec core / adapters /
  front-ends layering and the decisions that follow from it.
* [Enforcement](enforcement/index.md) - the Git hooks that make the
  convention unbypassable, and the division of labor between core, adapters,
  and front-ends.
* [Conventions](conventions/index.md) - commit and branch naming.
* [gitlint](gitlint/index.md) - the optional gitlint adapter: when to use
  it, how to install and configure it.
* [LLM-backed suggestions](suggestions/index.md) - the `jev` provider: what
  it sends, to whom, and how it fails.
* [MCP](mcp/index.md) - the Model Context Protocol server exposed to
  agents.
* [Toolchain](toolchain/index.md) - which layer (mise or an ecosystem
  package manager) installs which tool, and why.
* [Python](python/index.md) - decisions specific to this project's Python
  implementation.
* [Release](release/index.md) - how this project ships new versions to
  PyPI.

## Agents

* [Agents](agents/index.md) - install the skills in Claude Code, in
  `npx skills`, or in opencode, and learn what each channel delivers.

See [`log.md`](log.md) for the bundle's change history.
