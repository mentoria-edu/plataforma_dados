#!/bin/bash

# inicia os serviços do hadoop e ssh
service ssh start && start-dfs.sh

# Aguarda para iniciar o serviço do HDFS
sleep 10

# Cria e da permissão para pasta warehouse
sudo -u hdfs opt/hadoop/bin/hadoop fs -mkdir /warehouse
sudo -u hdfs opt/hadoop/bin/hadoop fs -chmod 777 /warehouse

# Mantém o contêiner rodando
tail -f /dev/null
