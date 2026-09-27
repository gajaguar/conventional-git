# Enforcement

How the convention is made unbypassable through Git hooks, and the division
of labor between the core, adapters, and front-ends.

* [Three enforcement surfaces](git-hooks.md) - the commit-msg, pre-commit,
  and pre-push hooks and what each rejects.
* [Where hooks are installed](hook-install-path.md) - worktrees,
  `core.hooksPath`, the `managed-by` marker, and `--force`.
* [Registering hooks with the pre-commit framework](pre-commit-framework.md) -
  the published `.pre-commit-hooks.yaml` hooks.
* [A repo:local pre-commit configuration](pre-commit-local-hooks.md) - an
  isolated environment alternative to a globally installed CLI.
* [CI recipe](ci-recipe.md) - the commands CI should run since local hooks
  can be bypassed with `--no-verify`.
* [Where the house rules live](house-rules.md) - all rules live in the core;
  there is no separate spec-checking tool.
* [Attribution trailers are rejected](attribution-trailers.md) -
  `Co-Authored-By:`, `Generated with …`, and 🤖 markers.
* [The commitizen adapter is opt-in](commitizen-adapter.md) - checks only
  the header's type/scope shape, and nothing wires it in by default.
* [Branch names are this project's differentiator](branch-name-gap.md) -
  neither gitlint nor commitizen validates branch names.
* [Skill vocabulary copies stay byte-identical](skill-vocabulary-copies.md) -
  why `skills/*/references/` ships its own CSV copy.
