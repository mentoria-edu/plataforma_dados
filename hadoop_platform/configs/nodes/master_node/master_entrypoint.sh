#!/bin/bash
set -e

if [ ! -f $HDFS_VERSION ]; then
    echo "Formatting NameNode for the first time..."
    hdfs namenode -format
fi

echo "Starting HDFS NameNode..."
hdfs --daemon start namenode

echo "Waiting for NameNode to start..."
sleep 5 
if ! pgrep -f "proc_namenode" > /dev/null; then
    echo "ERROR: NameNode did not start correctly!"
    echo "--- Last 20 lines of NameNode log ---"
    tail -20 $HADOOP_HOME/logs/hadoop-*-namenode-*.log
    exit 1
fi

echo "Checking port 9000..."
sleep 5

if ! netstat -tlnp | grep -q ":9000"; then
    echo "ERROR: NameNode is not listening on port 9000!"
    echo "--- Port status ---"
    netstat -tlnp
    exit 1
fi

echo "Waiting for HDFS to exit safe mode..."
attempt=0
max_attempts=5
while [ $attempt -lt $max_attempts ]; do
    if hdfs dfsadmin -safemode get | grep -q "Safe mode is OFF"; then
    echo "HDFS exited safe mode!"
    break
    fi
    attempt=$((attempt + 1))
    echo "Attempt $attempt/$max_attempts - HDFS still in safe mode..."
    sleep 5
    hdfs dfsadmin -safemode leave
done

if [ $attempt -lt $max_attempts ]; then
    echo "Creating directories in HDFS..."
    hadoop fs -mkdir -p /spark_events 
    hadoop fs -mkdir -p /lakehouse
    hadoop fs -mkdir -p /yarn_logs
    hadoop fs -mkdir -p /spark_events_log
    
    echo "Configuring Hive Metastore..."
    schematool -dbType postgres -info || schematool -dbType postgres -initSchema
    echo "Waiting for metastore to start..."

    echo "Starting Hive Metastore..."
    hive --service metastore > $HADOOP_HOME/logs/metastore.log 2>&1 &
    
    if [ ! -f " $HADOOP_HOME/logs/metastore.log" ]; then
    echo  "Hive Metastore initialized successfully!"
    fi


until hive -e "SHOW DATABASES;"; do
    sleep 2
done

echo  "Creating bronze schema in metastore"
hive -e "CREATE SCHEMA IF NOT EXISTS BRONZE;"
echo "Hadoop environment initialized successfully!"

echo "Starting YARN ResourceManager..."
yarn --daemon start resourcemanager
    
else
    echo "ERROR: HDFS did not exit safe mode after several attempts!"
    exit 1
fi

tail -f /dev/null