# Toolchain

Which layer — mise or an ecosystem package manager — installs which tool,
and why.

* [mise bootstraps, the ecosystem manager installs the rest](layering-rule.md) -
  the full tool-by-tool placement table.
* [Rejected install backends](rejected-install-backends.md) - the mise
  `npm:`/`pipx:` backends and pre-commit-managed environments this rules
  out.
* [The dev group self-references its own extras](extras-self-reference.md) -
  `conventional-git[gitlint,llm,mcp]`, not a second pin.
* [The sh advisory is dismissed](sh-uid-unused.md) - why the `sh` alert is
  not used here and which test reopens the question.
* [Re-tag the notes](retag-notes.md) - run `make docs-retag`, review the
  dry run, then write the tags.
