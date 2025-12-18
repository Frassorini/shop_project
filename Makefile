PID_DIR := .pids
LOG_DIR := logs

ENV_FILE_TEST := environment/.env.test
ENV_FILE_DEV := environment/.env.dev
ENV_FILE_PROD := environment/.env.prod
COMPOSE_TEST := docker compose -f docker-compose/docker-compose.test.yml
COMPOSE_DEV := docker compose -f docker-compose/docker-compose.dev.yml
COMPOSE_PROD := docker compose -f docker-compose/docker-compose.prod.yml
TASKIQ_TEST_CMD := env ENV_FILE=environment/.env.test taskiq worker \
	--ack-type when_saved \
	shop_project.taskiq_worker_broker:broker

help:
	@echo   Main commands:
	@echo   make dev-up        		    - Start dev infrastructure without application
	@echo   make test-up       		    - Start test infrastructure without application
	@echo   make prod-up       		    - Start prod infrastructure WITH application
	@echo   make dev-down      		    - Stop dev infrastructure without application
	@echo   make test-down     		    - Stop test infrastructure without application
	@echo   make prod-down     		    - Stop prod infrastructure WITH application
	@echo   make all-down      		    - Stop all containers
	@echo   make test                   - Run all tests unit + integration
	@echo   make unit-tests             - Run unit tests only
	@echo   make integration-tests      - Run integration tests only
	@echo   make format                 - Run pre-commit hooks
	@echo   make ci            		    - Start infrastructure and run tests
	@echo   make bg-workers-test-up     - Start test background workers
	@echo   make bg-workers-test-down   - Stop test background workers
	@echo   make bg-workers-test-reload - Reload test background workers

dev-up:
	$(COMPOSE_DEV) up -d

test-up:
	$(COMPOSE_TEST) up -d

prod-up:
	$(COMPOSE_PROD) up -d

dev-down:
	$(COMPOSE_DEV) down

test-down:
	$(COMPOSE_TEST) down

prod-down:
	$(COMPOSE_PROD) down

all-down:
	$(COMPOSE_DEV) down || true
	$(COMPOSE_TEST) down || true
	$(COMPOSE_PROD) down || true

unit-tests:
	ENV_FILE=$(ENV_FILE_TEST) poetry run pytest -v -s -m "not integration" 

integration-tests:
	ENV_FILE=$(ENV_FILE_TEST) poetry run pytest -v -s -m "integration" --real-db --real-broker

tests-with-integration:
	ENV_FILE=$(ENV_FILE_TEST) poetry run pytest -v -s --real-db --real-broker

test-bg-up-in-bg:
	@mkdir -p $(PID_DIR) $(LOG_DIR)
	@echo "Starting Taskiq workers in background..."
	@nohup $(TASKIQ_TEST_CMD) \
		> $(LOG_DIR)/taskiq-test.log 2>&1 & \
		echo $$! > $(PID_DIR)/taskiq-test.pid
	@echo "Taskiq started with PID $$(cat $(PID_DIR)/taskiq-test.pid)"

test-bg-down-in-bg:
	@if [ -f $(PID_DIR)/taskiq-test.pid ]; then \
		echo "Stopping Taskiq workers..."; \
		kill -TERM $$(cat $(PID_DIR)/taskiq-test.pid); \
		rm $(PID_DIR)/taskiq-test.pid; \
	else \
		echo "No running Taskiq workers"; \
	fi

test-bg-up:
	@echo "Starting Taskiq workers in interactive mode..."
	@$(TASKIQ_TEST_CMD)

bg-logs:
	@if [ -f $(LOG_DIR)/taskiq-test.log ]; then \
		tail -f $(LOG_DIR)/taskiq-test.log; \
	else \
		echo "Log file not found. Start workers first."; \
	fi

format:
	poetry run pre-commit run --all-files

ci: 
	$(MAKE) test-up
	$(MAKE) test-bg-up-in-bg
	$(MAKE) tests-with-integration
	$(MAKE) test-bg-down-in-bg
	$(MAKE) test-down