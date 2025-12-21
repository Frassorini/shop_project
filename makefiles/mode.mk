ifndef _MODE_MK_INCLUDED
_MODE_MK_INCLUDED := 1

include makefiles/config.mk

define validate_mode
$(if $(filter $(strip $1),$(VALID_MODES)),,$(error Invalid MODE=$1. Valid modes: $(VALID_MODES)))
endef

define get_mode
$(if $(MODE),$(call validate_mode,$(MODE))$(MODE),$(DEFAULT_MODE))
endef

define get_env_by_mode
$(call validate_mode,$1)$(if $(filter $1,TEST),$(ENV_FILE_TEST),$(if $(filter $1,DEV),$(ENV_FILE_DEV),$(ENV_FILE_PROD)))
endef

define get_database_container_name_by_mode
$(call validate_mode,$1)$(if $(filter $1,TEST),$(DATABASE_CONTAINER_NAME_TEST),$(if $(filter $1,DEV),$(DATABASE_CONTAINER_NAME_DEV),$(DATABASE_CONTAINER_NAME_PROD)))
endef

define get_maxwell_container_name_by_mode
$(call validate_mode,$1)$(if $(filter $1,TEST),$(MAXWELL_CONTAINER_NAME_TEST),$(if $(filter $1,DEV),$(MAXWELL_CONTAINER_NAME_DEV),$(MAXWELL_CONTAINER_NAME_PROD)))
endef

define get_compose_by_mode
$(call validate_mode,$1)$(if $(filter $1,TEST),$(COMPOSE_FILE_TEST),$(if $(filter $1,DEV),$(COMPOSE_FILE_DEV),$(COMPOSE_FILE_PROD)))
endef

define get_taskiq_broker_by_mode
$(call validate_mode,$1)$(if $(filter $1,TEST),$(TASKIQ_BROKER_TEST),$(if $(filter $1,DEV),$(TASKIQ_BROKER_DEV),$(TASKIQ_BROKER_PROD)))
endef

endif
