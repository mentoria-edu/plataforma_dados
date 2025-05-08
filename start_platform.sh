#!/bin/bash
set -e

echo "Verificando a instalação do Docker e do docker-compose"
if docker --version > /dev/null && docker compose --version > /dev/null; then
    docker build -f ./hadoop_platform/docker/base.Dockerfile -t "hadoop_platform" .
    docker compose -f ./hadoop_platform/compose/docker-compose.yaml up -d --build
else
    echo "Não há nenhuma versão de Docker ou do Docker compose instalado!"
    exit 1
fi