ifndef _BACKGROUND_MK_INCLUDED
_BACKGROUND_MK_INCLUDED := 1

include makefiles/config.mk
include makefiles/mode.mk
include makefiles/helpers.mk

# start_taskiq_bg: $(1)=mode, $(2)=PID_DIR, $(3)=LOG_DIR, $(4)=broker_path
define start_taskiq_bg
	@mkdir -p $(2) $(3)
	@if [ -f $(2)/taskiq-$(1).pid ] && kill -0 $$(cat $(2)/taskiq-$(1).pid) 2>/dev/null; then \
		echo "Taskiq for mode $(1) is already running with PID $$(cat $(2)/taskiq-$(1).pid)"; \
	else \
		echo "Starting Taskiq workers in background for mode $(1)..."; \
		nohup taskiq worker $(4) --ack-type when_saved > $(3)/taskiq-$(1).log 2>&1 & \
		echo $$! > $(2)/taskiq-$(1).pid; \
		echo "Taskiq started with PID $$(cat $(2)/taskiq-$(1).pid)"; \
	fi
endef

# stop_taskiq_bg: $(1)=mode, $(2)=PID_DIR
define stop_taskiq_bg
	@if [ -f $(2)/taskiq-$(1).pid ]; then \
		echo "Stopping Taskiq workers for mode $(1)..."; \
		kill -TERM $$(cat $(2)/taskiq-$(1).pid); \
		rm $(2)/taskiq-$(1).pid; \
	else \
		echo "No running Taskiq workers for mode $(1)"; \
	fi
endef

# tail_taskiq_log: $(1)=mode, $(2)=LOG_DIR
define tail_taskiq_log
	@if [ -f $(2)/taskiq-$(1).log ]; then \
		tail -f $(2)/taskiq-$(1).log; \
	else \
		echo "Log file not found for mode $(1). Start workers first."; \
	fi
endef

bg-up: ## Start Taskiq workers in background
	$(call ask_confirmation_if_prod)
	$(call start_taskiq_bg,$(call get_mode),$(PID_DIR),$(LOG_DIR),$(call get_taskiq_broker_by_mode,$(call get_mode)))

bg-down: ## Stop Taskiq workers in background
	$(call stop_taskiq_bg,$(call get_mode),$(PID_DIR))

bg-up-interactive: ## Start Taskiq workers in interactive mode
	$(call ask_confirmation_if_prod)
	@echo "Starting Taskiq workers in interactive mode..."
	taskiq worker $(call get_taskiq_broker_by_mode,$(call get_mode)) --ack-type when_saved

bg-reload: ## Reload Taskiq workers
	@$(MAKE) --no-print-directory bg-down
	@$(MAKE) --no-print-directory bg-up

bg-logs: ## Tail Taskiq logs
	$(call tail_taskiq_log,$(call get_mode),$(LOG_DIR))

bg-all-down: ## pkill taskiq
	$(call ask_confirmation,"Are you sure you want to stop all Taskiq workers?")
	$(foreach mode,$(VALID_MODES),$(call stop_taskiq_bg,$(mode),$(PID_DIR))$(newline))

endif


