#!/bin/bash

# Verifica se a variável de ambiente SPARK_MODE foi definida
if [ -z "$SPARK_MODE" ]; then
    echo "A variável de ambiente SPARK_MODE não está definida. Defina SPARK_MODE como 'master' ou 'worker'."
    exit 1
fi

# Caso a variável de ambiente SPARK_MODE seja "master"
if [ "$SPARK_MODE" == "master" ]; then
    echo "Iniciando o Spark Master..."
    sudo /opt/spark/sbin/start-master.sh && tail -f /dev/null
# Caso a variável de ambiente SPARK_MODE seja "worker"
elif [ "$SPARK_MODE" == "worker" ]; then
    echo "Iniciando o Spark Worker..."
    sudo /opt/spark/sbin/start-worker.sh spark://spark-master:7077 && tail -f /dev/null
else
    echo "Valor inválido para SPARK_MODE. Use 'master' ou 'worker'."
    exit 1
fi
