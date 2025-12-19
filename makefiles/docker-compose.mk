ifndef _DOCKER_COMPOSE_MK_INCLUDED
_DOCKER_COMPOSE_MK_INCLUDED := 1

include makefiles/config.mk
include makefiles/mode.mk
include makefiles/helpers.mk

define COMPOSE_UP
docker compose -f $(1) up -d
endef

define COMPOSE_DOWN
docker compose -f $(1) down
endef

compose-up: ## Up current mode compose
	$(call ask_confirmation_if_prod)
	$(call COMPOSE_UP,$(call get_compose_by_mode,$(call get_mode)))

compose-down: ## Down current mode compose
	$(call ask_confirmation_if_prod)
	$(call COMPOSE_DOWN,$(call get_compose_by_mode,$(call get_mode)))
	
all-down: ## Down all active composes of this project
	$(call ask_confirmation,"Are you sure you want to bring down all modes?")
	$(foreach mode,$(VALID_MODES),$(call COMPOSE_DOWN,$(call get_compose_by_mode,$(call get_mode)))$(newline))
	
endif