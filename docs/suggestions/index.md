# LLM-backed suggestions

The `jev` suggestion provider: what it sends, to whom, and how it fails.

* [What leaves your machine](data-egress.md) - the staged diff, file paths,
  and vocabulary sent to TypeSafe or OpenRouter.
* [Providers and credential resolution order](providers-and-credentials.md) -
  which credential talks to which endpoint and model.
* [Keyring scope and auth status](keyring-scope.md) - one key per provider,
  no plaintext fallback.
* [Failure modes: fallback versus hard failure](provider-fallback.md) -
  silent fallback unless `--provider jev` was explicit.
* [--apply renders, it does not commit](apply-does-not-commit.md) - pipe the
  result into `git commit -F -` yourself.
* [Installing the llm extra afterward](llm-extra-install.md) - `uv tool
  install --force '.[llm]'`.
