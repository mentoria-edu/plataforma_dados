#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

echo "Creating necessary directories..."
mkdir -p ${SCRIPT_DIR}/dags ${SCRIPT_DIR}/logs ${SCRIPT_DIR}/plugins ${SCRIPT_DIR}/config

echo "Configuring AIRFLOW_UID..."
if [ ! -f ${SCRIPT_DIR}/.env ]; then
  echo -e "AIRFLOW_UID=$(id -u)" > ${SCRIPT_DIR}/.env
  echo ".env file created with AIRFLOW_UID=$(id -u)"
else
  echo ".env file already exists, skipping creation"
fi

echo "Initializing Airflow database and creating admin user..."
docker compose -f ${SCRIPT_DIR}/docker-compose.yaml up airflow-init

if [ $? -eq 0 ]; then
  echo ""
  echo "Airflow initialization completed successfully!"
  echo ""
  echo "Starting Airflow services..."
  docker compose -f ${SCRIPT_DIR}/docker-compose.yaml up -d

else
  echo ""
  echo "Airflow initialization failed!"
  exit 1
fi