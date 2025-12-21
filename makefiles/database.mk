ifndef _DATABASE_MK_INCLUDED
_DATABASE_MK_INCLUDED := 1

include makefiles/config.mk
include makefiles/mode.mk
include makefiles/helpers.mk

db-init: ## Run docker/mysql/init.sh
	$(call ask_confirmation_if_prod)
	@env $(call load_env,$(ENV_FILE)) MYSQL_CONTAINER_NAME=$(call get_database_container_name_by_mode,$(call get_mode)) bash docker/mysql/init.sh

endif