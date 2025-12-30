ENV_FILE ?= environment/.env.test
export ENV_FILE

include makefiles/background.mk
include makefiles/tests.mk
include makefiles/docker-compose.mk
include makefiles/utils.mk
include makefiles/database.mk
include makefiles/app.mk

.DEFAULT_GOAL := help

help:  ## Show available commands
	@echo "Current MODE: $(if $(MODE),$(MODE),$(DEFAULT_MODE))"
	@grep -h -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "%-25s %s\n", $$1, $$2}'

