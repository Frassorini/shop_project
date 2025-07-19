.PHONY: help, dev-up, test-up, prod-up, dev-down, test-down, prod-down, all-down, test, unit-tests, integration-tests, ci

ENV_FILE_TEST := environment/.env.test
ENV_FILE_DEV := environment/.env.dev
ENV_FILE_PROD := environment/.env.prod
COMPOSE_TEST := docker-compose -f docker-compose/docker-compose.test.yml
COMPOSE_DEV := docker-compose -f docker-compose/docker-compose.dev.yml
COMPOSE_PROD := docker-compose -f docker-compose/docker-compose.prod.yml

help:
	@echo   Main commands:
	@echo   make dev-up        		- Start dev infrastructure (without application)
	@echo   make test-up       		- Start test infrastructure (without application)
	@echo   make prod-up       		- Start prod infrastructure (WITH application)
	@echo   make dev-down      		- Stop dev infrastructure (without application)
	@echo   make test-down     		- Stop test infrastructure (without application)
	@echo   make prod-down     		- Stop prod infrastructure (WITH application)
	@echo   make all-down      		- Stop all containers
	@echo   make test               - Run all tests (unit + integration)
	@echo   make unit-tests         - Run unit tests only
	@echo   make integration-tests  - Run integration tests only
	@echo   make ci            		- Start infrastructure and run tests

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

test:
	ENV_FILE=$(ENV_FILE_TEST) poetry run pytest -v -s

unit-tests:
	ENV_FILE=$(ENV_FILE_TEST) poetry run pytest -v -s -m "not integration"

integration-tests:
	ENV_FILE=$(ENV_FILE_TEST) poetry run pytest -v -s -m "integration"

ci: 
	$(MAKE) test-up
	poetry run pytest -v -s
	$(MAKE) test-down
