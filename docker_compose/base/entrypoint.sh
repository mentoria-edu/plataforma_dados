#!/bin/bash
set -euxo pipefail

# Configuração do hostname
# echo "127.0.0.1 masternode" >> /etc/hosts
echo "Iniciando serviço SSH..."
service ssh start

if [ "$CLIENT_NODE" == "false" ]; then

  if [ "$SPECIFIC_NODE" == "master" ]; then
    
    # Formatação do NameNode - CRUCIAL SE FOR A PRIMEIRA EXECUÇÃO
    if [ ! -f $VERSION_HDFS ]; then
      echo "Formatando o NameNode pela primeira vez..."
      hdfs namenode -format
    fi

    # Iniciar NameNode e verificar se está rodando
    echo "Iniciando HDFS NameNode..."
    hdfs --daemon start namenode

    # Verificar se o processo NameNode está executando
    echo "Aguardando NameNode iniciar..."
    sleep 5 
    if ! pgrep -f "proc_namenode" > /dev/null; then
      echo "ERRO: NameNode não iniciou corretamente!"
      # Para debug
      echo "--- Últimas 20 linhas do log do NameNode ---"
      tail -20 /opt/hadoop/logs/hadoop-*-namenode-*.log
      exit 1
    fi

    # Verificar se o NameNode está escutando na porta 9000
    echo "Verificando porta 9000..."
    sleep 5
    if ! netstat -tlnp | grep -q ":9000"; then
      echo "ERRO: NameNode não está escutando na porta 9000!"
      # Para debug
      echo "--- Status das portas ---"
      netstat -tlnp
      exit 1
    fi

    # Aguardar HDFS sair do modo seguro
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

    # Continuar com a criação de diretórios
    if [ $attempt -lt $max_attempts ]; then
      echo "Criando diretórios no HDFS..."
      hadoop fs -mkdir -p /spark_events 
      hadoop fs -mkdir -p /lakehouse
      hadoop fs -mkdir -p /yarn_logs
      hadoop fs -mkdir -p /spark_events_log
      # hadoop fs -chmod -R 777 /warehouse /spark_events /lakehouse /yarn_logs
      
      # Iniciar ResourceManager
      echo "Iniciando YARN ResourceManager..."
      yarn --daemon start resourcemanager

      # Inicializar Hive
      echo "Configurando Hive Metastore..."
      schematool -dbType postgres -info || schematool -dbType postgres -initSchema
      
      # Iniciar serviço Hive Metastore
      echo "Iniciando Hive Metastore..."
      hive --service metastore > /opt/hadoop/logs/metastore.log 2>&1 &
      if [ ! -f "/opt/hadoop/logs/metastore.log" ]; then
        echo  "Hive Metastore inicializado com sucesso!"
      fi
    else
      echo "ERRO: HDFS não saiu do modo seguro após várias tentativas!"
      exit 1
    fi
  
    echo "Ambiente Hadoop inicializado com sucesso!"

  elif [ "$SPECIFIC_NODE" == "worker" ]; then
    echo "Chamando o logs_yarn.sh..."
    bash ${HADOOP_HOME}/bin/logs_yarn.sh > /tmp/logs/logs_yarn.log 2>&1 &
    echo "Logs yarn chamado."

    chown -R ${UID}:${GID} /tmp/logs

    echo "Iniciando HDFS datanode..."
    hdfs --daemon start datanode 
    
    echo "Iniciando YARN nodemanager..."
    yarn --daemon start nodemanager
   
  else
    echo "Valor inválido para SPECIFIC_NODE. Use 'master', 'worker'."
    exit 1
  fi

elif [ "$CLIENT_NODE" == "true" ]; then
    echo "Container inicializado em modo Client. \
    Todos os arquivos de configurações estão presentes, \
    mas nada é inicializado" 

    ${SPARK_HOME}/bin/spark-submit  --master yarn --deploy-mode cluster ${SPARK_HOME}/examples/src/main/python/pi.py

else
  echo "Valor inválido para CLIENT_NODE. Use 'true' ou 'false'."
    exit 1
fi
tail -f /dev/null