UV := uv

LANG_CHECK_TARGETS      += conventional-git-check
LANG_TEST_TARGETS       += conventional-git-test

##@ conventional-git

conventional-git-check: ## Run conventional-git's own validation against a fixed sample message
	$(UV) run conventional-git check commit --message "feat: add login"

conventional-git-test: ## Smoke-test the conventional-git CLI end to end
	$(UV) run conventional-git --help
	$(UV) run conventional-git check commit --message "feat: add login"

.PHONY: conventional-git-check conventional-git-test
