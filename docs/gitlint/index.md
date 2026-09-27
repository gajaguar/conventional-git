# The gitlint extra

`adapters/gitlint_rules.py` is an optional adapter translating the core's
violations into gitlint's error type, not a second rule set.

* [When to reach for the gitlint extra](when-to-use.md) - already running
  gitlint, or checking a commit range in CI.
* [Installing the gitlint extra](install.md) - `--with-executables-from
  gitlint-core` puts `gitlint` on `PATH`.
* [Locating extra-path](extra-path.md) - a filesystem path, not an import
  name, and it changes on reinstall.
* [Recommended .gitlint config](recommended-config.md) - the `ignore` list
  and `[CG1] warnings = true`.
* [Behavior versus the CLI](behavior-vs-cli.md) - same verdict, same config
  file, no branch-name checking.
* [Wiring gitlint into a repo](wiring.md) - `install-hook`, a `repo: local`
  entry, or a CI range check.
