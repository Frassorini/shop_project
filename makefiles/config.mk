ifndef _CONFIG_MK_INCLUDED
_CONFIG_MK_INCLUDED := 1

override VALID_MODES := TEST DEV PROD
override DEFAULT_MODE := TEST

override PID_DIR := .pids
override LOG_DIR := logs

override ENV_FILE_TEST := environment/.env.test
override ENV_FILE_DEV := environment/.env.dev
override ENV_FILE_PROD := environment/.env.prod

override DATABASE_CONTAINER_NAME_TEST := test-mysql
override DATABASE_CONTAINER_NAME_DEV := test-mysql
override DATABASE_CONTAINER_NAME_PROD := test-mysql

override MAXWELL_CONTAINER_NAME_TEST := test-maxwell
override MAXWELL_CONTAINER_NAME_DEV := test-maxwell
override MAXWELL_CONTAINER_NAME_PROD := test-maxwell


override COMPOSE_FILE_TEST := docker-compose/docker-compose.test.yml
override COMPOSE_FILE_DEV  := docker-compose/docker-compose.dev.yml
override COMPOSE_FILE_PROD := docker-compose/docker-compose.prod.yml

override TASKIQ_BROKER_TEST := shop_project.taskiq_worker_broker:broker
override TASKIQ_BROKER_DEV := shop_project.taskiq_worker_broker:broker
override TASKIQ_BROKER_PROD := shop_project.taskiq_worker_broker:broker

endif