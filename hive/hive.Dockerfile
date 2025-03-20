FROM ubuntu:22.04

# Instalação do Java pois é um pré-requisito para o funcionamento e o curl para fazer o download do  hadoop
RUN apt update && apt install -y \
    openjdk-8-jdk \
    wget 

# Baixa o hadoop - Descompacta na pasta /opt - renomeia a pasta para /opt/hadoop
RUN wget https://dlcdn.apache.org/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz && \
    tar -xvzf hadoop-3.3.6.tar.gz -C /opt && \
    mv /opt/hadoop-3.3.6 /opt/hadoop

# Baixa o hive - Descompacta na pasta /opt - renomeia a pasta para /opt/hive
RUN wget https://dlcdn.apache.org/hive/hive-4.0.1/apache-hive-4.0.1-bin.tar.gz && \
    tar -xvzf apache-hive-4.0.1-bin.tar.gz -C /opt && \
    mv /opt/apache-hive-4.0.1-bin /opt/hive

# Definir variáveis de ambiente para o Hive
ENV HIVE_HOME=/opt/hive
ENV PATH=$PATH:$HIVE_HOME/bin
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
ENV HADOOP_HOME=/opt/hadoop
RUN echo "Export HADOOP_HOME=/opt/hadoop" >> /opt/hive/bin/hive_config.sh

# Copiando arquivos de configuração
COPY hive-site.xml /opt/hive/conf

EXPOSE 9083

CMD ["/bin/bash", "-c", "hive --metastore && tail -f /dev/null"]
