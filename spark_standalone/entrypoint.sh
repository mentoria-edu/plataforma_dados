#!/bin/bash

# Verifica se a variável de ambiente SPARK_MODE foi definida
if [ -z "$SPARK_MODE" ]; then
    echo "A variável de ambiente SPARK_MODE não está definida. Defina SPARK_MODE como 'master', 'worker' ou 'history'."
    exit 1
fi

# Caso a variável de ambiente SPARK_MODE seja "master"
if [ "$SPARK_MODE" == "master" ]; then
    echo "Iniciando o Spark Master..."
    bash /opt/spark/sbin/start-master.sh -p 7077
# Caso a variável de ambiente SPARK_MODE seja "worker"
elif [ "$SPARK_MODE" == "worker" ]; then
    echo "Iniciando o Spark Worker..."
    bash /opt/spark/sbin/start-worker.sh spark://spark-master:7077

elif [ "$SPARK_MODE" == "history" ]
then
    echo "Iniciando o Spark History..."
    bash /opt/spark/bin/spark-submit --master spark://spark-master:7077 --deploy-mode client /opt/spark/examples/src/main/python/pi.py && /opt/spark/sbin/start-history-server.sh

else
    echo "Valor inválido para SPARK_MODE. Use 'master', 'worker', 'history' ou 'spark-shell'."
    exit 1
fi
