UV := uv
BASE ?= origin/main

LANG_CHECK_TARGETS      += conventional-git-check
LANG_TEST_TARGETS       += conventional-git-test hooks-selftest

##@ conventional-git

conventional-git-check: ## Validate this repo's own commit history and branch name against its rules
	@git log --format='%B%x00' $(BASE)..HEAD | while IFS= read -r -d '' message; do \
		[ -z "$$message" ] && continue; \
		echo "$$message" | $(UV) run conventional-git check commit || exit 1; \
	done
	$(UV) run conventional-git check branch --name "$${GITHUB_HEAD_REF:-$$(git branch --show-current)}"

conventional-git-test: ## Smoke-test the conventional-git CLI end to end
	$(UV) run conventional-git --help
	$(UV) run conventional-git check commit --message "feat: add login"

hooks-selftest: ## Run the published pre-commit hooks against this working tree
	@msg=$$(mktemp) && echo "feat: add login" > "$$msg" && \
		$(UV) run pre-commit try-repo . conventional-commit-msg \
			--hook-stage commit-msg --commit-msg-filename "$$msg"; \
		status=$$?; rm -f "$$msg"; exit $$status
	$(UV) run pre-commit try-repo . conventional-branch-name --hook-stage pre-commit

.PHONY: conventional-git-check conventional-git-test hooks-selftest
