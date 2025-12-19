ifndef _MODE_MK_INCLUDED
_MODE_MK_INCLUDED := 1

define validate_mode
$(if $(filter $(MODE),$(VALID_MODES)),,$(error Invalid MODE=$(MODE). Valid modes: $(VALID_MODES)))
endef

define get_mode
$(if $(MODE),$(call validate_mode,$(MODE))$(MODE),$(DEFAULT_MODE))
endef

define get_env_by_mode
$(call validate_mode,$1)$(if $(filter $1,TEST),$(ENV_FILE_TEST),$(if $(filter $1,DEV),$(ENV_FILE_DEV),$(ENV_FILE_PROD)))
endef

define get_taskiq_broker_by_mode
$(call validate_mode,$1)$(if $(filter $1,TEST),$(TASKIQ_BROKER_TEST),$(if $(filter $1,DEV),$(TASKIQ_BROKER_DEV),$(TASKIQ_BROKER_PROD)))
endef

define get_compose_by_mode
$(call validate_mode,$1)$(if $(filter $1,TEST),$(COMPOSE_FILE_TEST),$(if $(filter $1,DEV),$(COMPOSE_FILE_DEV),$(COMPOSE_FILE_PROD)))
endef

endif
