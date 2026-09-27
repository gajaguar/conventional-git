# Toolchain

Which layer — mise or an ecosystem package manager — installs which tool,
and why.

* [mise bootstraps, the ecosystem manager installs the rest](layering-rule.md) -
  the full tool-by-tool placement table.
* [Rejected install backends](rejected-install-backends.md) - the mise
  `npm:`/`pipx:` backends and pre-commit-managed environments this rules
  out.
* [mise pins the high-level toolchain](mise.md) - Node, pnpm, pre-commit,
  and the Python runtime.
* [markdownlint-cli2 and cspell](markdown-tooling.md) - Markdown lint and
  spell check.
* [checkmake lints the Makefile](checkmake.md) - a Go binary with no
  ecosystem in this repo.
* [pre-commit runs the shared checks](pre-commit.md) - the git hook
  framework running the shared checks.
* [The dev group self-references its own extras](extras-self-reference.md) -
  `conventional-git[gitlint,llm,mcp]`, not a second pin.
