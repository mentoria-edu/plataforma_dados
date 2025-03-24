#FROM ubuntu:22.04 

FROM eclipse-temurin:11-jre-jammy

RUN apt update -y && \ 
    apt upgrade -y && \
    apt install -y \ 
    rsync \
    wget \
    ssh \
    tini \ 
    krb5-user \ 
    libnss3 \ 
    net-tools 


ENV SPARK_HOME=${SPARK_HOME:-"/opt/spark"}
ENV HADOOP_HOME=${HADOOP_HOME:-"/opt/hadoop"}

RUN mkdir -p ${HADOOP_HOME} && mkdir -p ${SPARK_HOME}


RUN wget https://dlcdn.apache.org/spark/spark-3.5.5/spark-3.5.5-bin-hadoop3.tgz

RUN tar xvf spark-3.5.5-bin-hadoop3.tgz && \
    mv spark-3.5.5-bin-hadoop3/* /opt/spark && \
    rm -r spark-3.5.5-bin-hadoop3.tgz


ENV SPARK_MODE="master"
ENV PATH="/opt/spark/sbin:/opt/spark/bin:${PATH}"


COPY entrypoint.sh /opt/spark/conf/entrypoint.sh
COPY spark-env.sh /opt/spark/conf/spark-env.sh
COPY spark-defaults.conf /opt/spark/conf/spark-defaults.conf

RUN mkdir -p /opt/spark/spark-events

# ENTRYPOINT [ "bash", "/opt/spark/conf/entrypoint.sh" ]