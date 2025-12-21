#!/bin/bash
set -e

if [ "$MAXWELL_PRODUCER" = "rabbitmq" ]; then
  echo "Waiting for RabbitMQ at ${MAXWELL_RABBITMQ_HOST}:${MAXWELL_RABBITMQ_PORT}..."

  while ! (echo > /dev/tcp/$MAXWELL_RABBITMQ_HOST/$MAXWELL_RABBITMQ_PORT) 2>/dev/null; do
    sleep 2
  done

  echo "RabbitMQ is up — starting Maxwell"
fi

exec bin/maxwell --env_config_prefix=MAXWELL_
