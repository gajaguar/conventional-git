UV := uv

LANG_CHECK_TARGETS      += conventional-kit-check
LANG_TEST_TARGETS       += conventional-kit-test

##@ conventional-kit

conventional-kit-check: ## Run conventional-kit's own validation against a fixed sample message
	$(UV) run conventional-kit check commit --message "feat: add login"

conventional-kit-test: ## Smoke-test the conventional-kit CLI end to end
	$(UV) run conventional-kit --help
	$(UV) run conventional-kit check commit --message "feat: add login"

.PHONY: conventional-kit-check conventional-kit-test
