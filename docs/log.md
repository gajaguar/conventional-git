# Directory Update Log

## 2026-09-28

* **Change**: The plugin's `.mcp.json`, the pre-commit hooks and the
  `Makefile` now resolve `conventional-git` from PyPI at `@latest` instead of
  a pinned version or the editable local install; updated
  `docs/mcp/plugin-bundled-server.md` to match.
* **Pruning**: Removed `docs/toolchain/{checkmake,markdown-tooling,mise,
  pre-commit}.md` and `docs/python/{docstring-policy,pylint-plugin}.md` —
  each only restated what `make help` or a linter's own message already
  says. Folded `docs/python/commit-range-in-ci.md` into
  `docs/conventions/commits-check.md`, and dropped `AGENTS.md`'s
  "Repository metadata" section (an instantiation-only checklist, stale
  since this project's first release), which had also leaked a scaffold
  tool's own name in its wording.

## 2026-09-26

* **Addition**: Added `docs/release/`, documenting the new
  `.github/workflows/publish.yml` and its use of PyPI Trusted Publishing
  (OIDC) triggered by a GitHub Release.
* **Restructuring**: Split `docs/` from eight flat, multi-topic files
  (`architecture.md`, `conventions.md`, `enforcement.md`, `gitlint.md`,
  `llm.md`, `mcp.md`, `python.md`, `toolchain.md`) into an
  [OKF](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
  bundle of atomic notes. `docs/conventions/` keeps only
  `commits-and-branches.md`, since it documents how this project itself
  enforces the Conventional Commits/Conventional Branch specs via its own
  hooks; the Makefile-scaffold conventions it used to share space with are
  documented once, outside this repository, rather than duplicated here.

## 2026-09-27

* **Addition**: Added `docs/conventions/commits-check.md`, documenting the
  two-layer enforcement (pre-commit hooks + `make commits-check` in CI) and
  this project's `CONVENTIONAL_GIT` override to run its own pinned
  dependency in CI instead of `uvx`.
