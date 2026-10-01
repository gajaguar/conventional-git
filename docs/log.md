# Directory Update Log

## 2026-09-30

* **Change**: [`conventions/commits-check.md`](conventions/commits-check.md)
  now says `make commits-check` skips merge commits and lists the valid
  branch types, with documentation and dependency work on `chore/`.

* **Addition**: Added [`conventions/help-check.md`](conventions/help-check.md)
  and [`conventions/claude-md-check.md`](conventions/claude-md-check.md) for
  the `make help-check` and `make claude-md-check` targets, now part of
  `make check`. Updated [`conventions/index.md`](conventions/index.md).

## 2026-09-29 (5)

* **Addition**: Added `docs/agents/` with this project's own
  `plugin-identity.md` (marketplace `conventional-git-skills`, plugin
  `conventional-git`, MCP server `conventional-git`, plus trigger
  phrasing for `conventional-commit` and `conventional-branch`) and
  `opencode-mcp-server.md` (a copy-ready `~/.config/opencode/config.json`
  snippet that launches the same `uvx` command as the bundled
  `.mcp.json`). Updated `docs/index.md`, cross-linked from
  `docs/mcp/plugin-bundled-server.md` and `docs/mcp/index.md`, and
  trimmed the README's Agents section to one command per channel.

## 2026-09-29 (4)

* **Addition**: [`toolchain/sh-uid-unused.md`](toolchain/sh-uid-unused.md)
  records why the Dependabot alert on `sh` is dismissed as not used, and
  `tests/test_sh_uid_unused.py` fails if `gitlint` or `src/` starts passing
  `_uid`.

## 2026-09-29 (3)

* **Change**: The `mcp` extra now requires `mcp>=2.2,<3`. `mcp/server.py`
  builds an `MCPServer` (`mcp.server.mcpserver`), the name `FastMCP` took in
  2.x; the tools and their contract are unchanged. Updated
  [`architecture/three-layers.md`](architecture/three-layers.md) and
  [`architecture/optional-extras.md`](architecture/optional-extras.md).

## 2026-09-29 (2)

* **Change**: `pylint-plugin` (a git dependency whose package was renamed,
  which broke `make install`) is replaced by `pylint-gajaguar` from PyPI, and
  `pyproject.toml` enables it with `enable = ["gajaguar"]`. The `dependabot/*`
  skip in `make commits-check` is gone: the project's own 1.1.0 accepts
  `dependabot/` and `renovate/` branch names. Updated
  [`conventions/commits-check.md`](conventions/commits-check.md).

## 2026-09-29

* **Addition**: Branch names starting with a prefix listed in
  `data/branch-exempt-prefixes.csv` (`dependabot/`, `renovate/`) now pass
  `check branch`, extendable through `[branch] exempt_prefix_overrides` and
  `--exempt-prefixes-csv`; recorded in
  [`architecture/vocabulary-as-data.md`](architecture/vocabulary-as-data.md).

## 2026-09-28 (2)

* **Addition**: Added `.github/dependabot.yml` (GitHub Actions, uv, npm,
  weekly). [`conventions/commits-check.md`](conventions/commits-check.md)
  now records that `make commits-check` skips the branch-name check for
  Dependabot's `dependabot/*` branches.

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
