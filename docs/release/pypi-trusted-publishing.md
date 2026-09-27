---
type: decision
title: PyPI releases use Trusted Publishing
description: The publish workflow uploads to PyPI via OIDC trusted publishing triggered by a GitHub Release, not a long-lived API token.
tags: [release, ci]
status: stable
---

# PyPI releases use Trusted Publishing

Publishing a GitHub Release (`published` event) runs
[`.github/workflows/publish.yml`](../../.github/workflows/publish.yml):
it builds the sdist and wheel with `make build`, then uploads them with
[`pypa/gh-action-pypi-publish`](https://github.com/pypa/gh-action-pypi-publish)
under the `pypi` environment. The publish job authenticates with a
short-lived OIDC token instead of a stored `PYPI_API_TOKEN`, so no PyPI
secret exists anywhere in this repository.

## One-time PyPI-side setup

Before the first release, add this workflow as a trusted publisher on the
PyPI project (`https://pypi.org/manage/project/conventional-git/publishing/`,
or the "pending publisher" form under
`https://pypi.org/manage/account/publishing/` if the project does not exist
on PyPI yet):

* Owner: `gajaguar`
* Repository name: `conventional-git`
* Workflow name: `publish.yml`
* Environment name: `pypi`

## Cutting a release

Bump `project.version` in `pyproject.toml`, then publish a GitHub Release
from a tag matching that version; the workflow does the rest.
