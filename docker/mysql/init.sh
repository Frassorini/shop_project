#!/bin/bash
set -euo pipefail

required_vars=(
  MYSQL_CONTAINER_NAME
  MYSQL_ROOT_PASSWORD
  MYSQL_DATABASE
  CDC_USER
  CDC_PASSWORD
)

for var in "${required_vars[@]}"; do
  if [[ -z "${!var:-}" ]]; then
    echo "ERROR: env var $var is not set"
    exit 1
  fi
done

: "${TEMPLATE_PATH:=docker/mysql/init.sql.tpl}"

if [[ ! -f "$TEMPLATE_PATH" ]]; then
  echo "ERROR: SQL template $(basename "$TEMPLATE_PATH") file not found!"
  exit 1
fi

envsubst < "$TEMPLATE_PATH" | docker exec -i -e MYSQL_PWD="$MYSQL_ROOT_PASSWORD" "$MYSQL_CONTAINER_NAME" \
  mysql -u root "$MYSQL_DATABASE" \
  && unset MYSQL_PWD

