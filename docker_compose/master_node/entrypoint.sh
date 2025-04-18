#!/bin/bash

set -e 

#hive --metastore

service ssh start && hdfs --daemon start namenode && yarn --daemon start resourcemanager

until hdfs dfsadmin -safemode get | grep "Safe mode is OFF"; do
  echo "Aguardando o HDFS sair do modo seguro..."
done

hadoop fs -mkdir -p /warehouse && \
hadoop fs -mkdir -p /spark_events && \
hadoop fs -mkdir -p /lakehouse  && \
hadoop fs -mkdir -p /yarn_logs

schematool -dbType postgres -info || schematool -dbType postgres -initSchema

tail -f /dev/null
