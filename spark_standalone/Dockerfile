FROM ubuntu:22.04 

ENV SPARK_MODE="master"

RUN apt update -y && \ 
    apt upgrade -y && \
    apt install -y \ 
    curl \
    sudo \
    wget \
    default-jdk

RUN wget https://dlcdn.apache.org/spark/spark-3.5.5/spark-3.5.5-bin-hadoop3.tgz

RUN tar xvf spark-3.5.5-bin-hadoop3.tgz && \
    mv spark-3.5.5-bin-hadoop3 /opt/spark && \
    rm -r spark-3.5.5-bin-hadoop3.tgz

RUN adduser --disabled-password ubuntu && \
    usermod -aG sudo ubuntu && \
    echo "ubuntu ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

RUN echo "export SPARK_HOME=/opt/spark" >> home/ubuntu/.bashrc && \
    echo "export PATH=\$PATH:\$SPARK_HOME/bin" >> home/ubuntu/.bashrc 

COPY entrypoint.sh /home/ubuntu/entrypoint.sh
RUN chmod +x /home/ubuntu/entrypoint.sh

USER ubuntu
WORKDIR /home/ubuntu

ENTRYPOINT ["/home/ubuntu/entrypoint.sh"]