#!/usr/bin/env bash

CONTAINER_NAME="postgres-test"

# Проверяем, запущен ли контейнер
if docker ps -a --format '{{.Names}}' | grep -Eq "^${CONTAINER_NAME}$"; then
    echo "Stopping and removing existing container: $CONTAINER_NAME"
    docker stop $CONTAINER_NAME > /dev/null 2>&1
    docker rm $CONTAINER_NAME > /dev/null 2>&1
fi

# Запускаем новый контейнер
echo "Starting a new container: $CONTAINER_NAME"
docker run -d --name $CONTAINER_NAME -p 5432:5432 postgres-test