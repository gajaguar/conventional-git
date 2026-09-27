# Directory Update Log

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

* **Addition**: Added `docs/conventions/commits-check.md` and
  `docs/python/commit-range-in-ci.md`, documenting the two-layer enforcement
  (pre-commit hooks + `make commits-check` in CI) that project-template now
  ships to every generated project, and this project's `CONVENTIONAL_GIT`
  override to run its own pinned dependency in CI instead of `uvx`.
