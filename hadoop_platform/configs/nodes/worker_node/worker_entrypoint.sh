#!/bin/bash
set -e

echo "Iniciando HDFS datanode..."
hdfs --daemon start datanode 

echo "Iniciando YARN nodemanager..."
yarn --daemon start nodemanager

echo "Inicializando os logs do sistema.."
bash logs_yarn.sh > $HADOOP_HOME/logs/logs_yarn.log 2>&1 &
echo "passou"

tail -f /dev/null