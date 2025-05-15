#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

echo "Checking Docker and docker-compose installation"
if ! command -v docker &>/dev/null; then
  echo "Docker is not installed!"
  exit 1
fi
if ! docker compose version &>/dev/null; then
  echo "Docker Compose is not installed!"
  exit 1
fi
echo "Docker and Docker Compose found successfully."

DOCKERFILE_PATH="${SCRIPT_DIR}/hadoop_platform/docker/base.Dockerfile"
COMPOSE_PATH="${SCRIPT_DIR}/hadoop_platform/compose/docker-compose.yaml"

if [ ! -f "$DOCKERFILE_PATH" ]; then
  echo "Error: Dockerfile not found at $DOCKERFILE_PATH"
  exit 1
fi

if [ ! -f "$COMPOSE_PATH" ]; then
  echo "Error: docker-compose.yaml not found at $COMPOSE_PATH"
  exit 1
fi

export HADOOP_PLATFORM_UID=$(id -u)
export HADOOP_PLATFORM_GID=$(id -g)

echo "Building the Hadoop base image..."
docker build -f "$DOCKERFILE_PATH" --build-arg -t "hadoop_platform" "$SCRIPT_DIR"

echo "Starting services with Docker Compose..."
docker compose -f "$COMPOSE_PATH" up --build 