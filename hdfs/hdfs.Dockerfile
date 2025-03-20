FROM ubuntu:22.04

# Instalação do Java pois é um pré-requisito para o funcionamento e o curl para fazer o download do  hadoop
RUN apt update && apt install -y \
    openjdk-8-jdk \
    wget \
    sudo \
    openssh-client \
    openssh-server


# Baixa o hadoop - Descompacta na pasta /opt - renomeia a pasta para /opt/hadoop
RUN wget https://dlcdn.apache.org/hadoop/common/hadoop-3.4.1/hadoop-3.4.1.tar.gz && \
    tar -xvzf hadoop-3.4.1.tar.gz -C /opt && \
    mv /opt/hadoop-3.4.1 /opt/hadoop

# Criação do usuário hadoop
RUN adduser --gecos "" --disabled-password hdfs && usermod -aG sudo hdfs

# Permissões para o usuário hadoop
RUN chown -R hdfs:hdfs /opt/hadoop

# Criação de Variavel de ambiente 
ENV HADOOP_HOME=/opt/hadoop
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
ENV HDFS_NAMENODE_USER=hdfs
ENV HDFS_DATANODE_USER=hdfs
ENV HDFS_SECONDARYNAMENODE_USER=hdfs
RUN echo "export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64" >> /opt/hadoop/etc/hadoop/hadoop-env.sh

# Formatando o NameNode para criação dos diretorios necessários
RUN hdfs namenode -format

# Criar diretório .ssh e gerar a chave SSH
RUN mkdir -p /home/hdfs/.ssh && \
    ssh-keygen -t rsa -P '' -f /home/hdfs/.ssh/id_rsa && \
    cat /home/hdfs/.ssh/id_rsa.pub >> /home/hdfs/.ssh/authorized_keys && \
    chmod 700 /home/hdfs/.ssh && \
    chmod 600 /home/hdfs/.ssh/authorized_keys && \
    chown -R hdfs:hdfs /home/hdfs/.ssh

# Copiar os arquivos XML de configuração para o contêiner
COPY core-site.xml /opt/hadoop/etc/hadoop/core-site.xml
COPY hdfs-site.xml /opt/hadoop/etc/hadoop/hdfs-site.xml


# Expor portas necessárias
EXPOSE 9870 9864

COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]