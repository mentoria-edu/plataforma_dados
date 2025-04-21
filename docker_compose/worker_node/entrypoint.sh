#!/bin/bash

set -e 

# echo "172.20.0.3 masternode" >> /etc/hosts

service ssh start && hdfs --daemon start datanode && yarn --daemon start nodemanager

tail -f /dev/null
