ifndef _TESTS_MK_INCLUDED
_TESTS_MK_INCLUDED := 1

include makefiles/config.mk
include makefiles/mode.mk

define RUN_TESTS
ENV_FILE=$(ENV_FILE_TEST) poetry run pytest -v -s $(1)
endef

tests-unit: ## Run unit tests only
	$(call RUN_TESTS,-m "not integration")

tests-integraiton-only: ## Run integration tests only
	$(call RUN_TESTS,-m "integration and not inmemory" --real-db --real-broker)

tests-with-integration: ## Run all tests including integration
	$(call RUN_TESTS, -m "not inmemory" --real-db --real-broker)

endif
