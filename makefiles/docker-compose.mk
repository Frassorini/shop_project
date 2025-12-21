ifndef _DOCKER_COMPOSE_MK_INCLUDED
_DOCKER_COMPOSE_MK_INCLUDED := 1

include makefiles/config.mk
include makefiles/mode.mk
include makefiles/helpers.mk
include makefiles/database.mk

define COMPOSE_UP
docker compose -f $(1) up -d
endef

define COMPOSE_DOWN
docker compose -f $(1) down
endef

define wait-for-mysql
@until docker exec $(1) \
	mysqladmin ping -h localhost -u root --silent; do \
	echo "Waiting for MySQL..."; \
	sleep 2; \
done
endef


compose-up: ## Up current mode compose
	$(call ask_confirmation_if_prod)
	$(call COMPOSE_UP,$(call get_compose_by_mode,$(call get_mode)))

	@echo "Waiting for MySQL to be ready..."
	$(call wait-for-mysql,$(call get_database_container_name_by_mode,$(call get_mode)))

	@echo "Initializing DB..."
	@env $(call load_env,$(ENV_FILE)) \
		MYSQL_CONTAINER_NAME=$(call get_database_container_name_by_mode,$(call get_mode)) \
		bash docker/mysql/init.sh

compose-down: ## Down current mode compose
	$(call ask_confirmation_if_prod)
	$(call COMPOSE_DOWN,$(call get_compose_by_mode,$(call get_mode)))
	
all-down: ## Down all active composes of this project
	$(call ask_confirmation,"Are you sure you want to bring down all modes?")
	$(foreach mode,$(VALID_MODES),$(call COMPOSE_DOWN,$(call get_compose_by_mode,$(call get_mode)))$(newline))
	
endif