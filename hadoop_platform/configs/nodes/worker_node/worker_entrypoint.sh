#!/bin/bash
set -e

echo "Starting HDFS Datanode..."
hdfs --daemon start datanode 

echo "Starting YARN Nodemanager..."
yarn --daemon start nodemanager

echo "Initializing the system logs..."
bash logs_yarn.sh > $HADOOP_HOME/logs/logs_yarn.log 2>&1 &

tail -f /dev/null