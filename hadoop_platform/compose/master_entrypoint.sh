#!/bin/bash
set -e

if [ ! -f $VERSION_HDFS ]; then
    echo "Formatando o NameNode pela primeira vez..."
    hdfs namenode -format
fi

echo "Iniciando HDFS NameNode..."
hdfs --daemon start namenode

echo "Aguardando NameNode iniciar..."
sleep 5 
if ! pgrep -f "proc_namenode" > /dev/null; then
    echo "ERRO: NameNode não iniciou corretamente!"
    echo "--- Últimas 20 linhas do log do NameNode ---"
    tail -20 /opt/hadoop/logs/hadoop-*-namenode-*.log
    exit 1
fi

echo "Verificando porta 9000..."
sleep 5

if ! netstat -tlnp | grep -q ":9000"; then
    echo "ERRO: NameNode não está escutando na porta 9000!"
    echo "--- Status das portas ---"
    netstat -tlnp
    exit 1
fi

echo "Aguardando o HDFS sair do modo seguro..."
attempt=0
max_attempts=30
while [ $attempt -lt $max_attempts ]; do
    if hdfs dfsadmin -safemode get | grep -q "Safe mode is OFF"; then
    echo "HDFS saiu do modo seguro!"
    break
    fi
    attempt=$((attempt + 1))
    echo "Tentativa $attempt/$max_attempts - HDFS ainda em modo seguro..."
    sleep 5
    hdfs dfsadmin -safemode leave
done

if [ $attempt -lt $max_attempts ]; then
    echo "Criando diretórios no HDFS..."
    hadoop fs -mkdir -p /spark_events 
    hadoop fs -mkdir -p /lakehouse
    hadoop fs -mkdir -p /yarn_logs
    hadoop fs -mkdir -p /spark_events_log
    
    echo "Iniciando Hive Metastore..."
    hive --service metastore > /opt/hadoop/logs/metastore.log 2>&1 &
    
    if [ ! -f "/opt/hadoop/logs/metastore.log" ]; then
    echo  "Hive Metastore inicializado com sucesso!"
    fi

echo "Configurando Hive Metastore..."
schematool -dbType postgres -info || schematool -dbType postgres -initSchema
echo "Esperando o metastore subir..."

until hive -e "SHOW DATABASES;" &> /dev/null; do
    sleep 2
done

echo  "Criando Schema bronze no metastore"
hive -e "CREATE SCHEMA IF NOT EXISTS bronze;"
echo "Ambiente Hadoop inicializado com sucesso!"

echo "Iniciando YARN ResourceManager..."
yarn --daemon start resourcemanager
    
else
    echo "ERRO: HDFS não saiu do modo seguro após várias tentativas!"
    exit 1
fi

tail -f /dev/null