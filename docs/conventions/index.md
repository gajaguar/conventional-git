# Conventions

Commit and branch naming.

* [Commits and branches follow published specs](commits-and-branches.md) -
  Conventional Commits and Conventional Branch, enforced by this project's
  own hooks.
* [Enforcing commits and branches](commits-check.md) - the pre-commit hook
  and `make commits-check` that enforce them.
* [Help-line check](help-check.md) - `make help-check` fails on a Makefile
  target without a `##` help line.
* [No CLAUDE.md check](claude-md-check.md) - `make claude-md-check` fails
  when a `CLAUDE.md` exists, since `AGENTS.md` is the only agent file.
