#!/bin/bash

set -e 

service ssh start && hdfs --daemon start datanode && yarn --daemon start nodemanager

tail -f /dev/null
