FROM eclipse-temurin:8-jdk-jammy

ARG V_HADOOP=3.4.1
ARG V_SPARK=3.5.5
ARG HADOOP_DIR=/opt/hadoop

ENV HADOOP_HOME=${HADOOP_DIR}
ENV SPARK_HOME=/opt/spark
ENV HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop
ENV YARN_CONF_DIR=/opt/hadoop/etc/hadoop
ENV USER_HDFS=root
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
ENV USER_HOME=/home/$USER_HDFS
ENV HDFS_NAMENODE_USER=$USER_HDFS
ENV HDFS_DATANODE_USER=$USER_HDFS
ENV HDFS_SECONDARYNAMENODE_USER=$USER_HDFS

RUN apt update && apt install -y \   
    wget \
    openssh-client \
    openssh-server

RUN wget https://dlcdn.apache.org/hadoop/common/hadoop-${V_HADOOP}/hadoop-${V_HADOOP}.tar.gz && \
    tar -xvzf hadoop-${V_HADOOP}.tar.gz -C /opt && \
    mv /opt/hadoop-${V_HADOOP} $HADOOP_HOME

RUN wget https://dlcdn.apache.org/spark/spark-${V_SPARK}/spark-${V_SPARK}-bin-hadoop3.tgz && \         
    tar -xvzf spark-${V_SPARK}-bin-hadoop3.tgz -C /opt && \
    mv /opt/spark-${V_SPARK}-bin-hadoop3 $SPARK_HOME 

RUN echo "export JAVA_HOME=${JAVA_HOME}" >> $HADOOP_HOME/etc/hadoop/hadoop-env.sh

#RUN adduser --gecos "" --disabled-password $USER_HDFS && \
#    usermod -aG sudo $USER_HDFS && \
#    chown -R $USER_HDFS:$USER_HDFS ${USER_HOME} && \
#    adduser --gecos "" --disabled-password hive 

#RUN chown -R $USER_HDFS:$USER_HDFS $HADOOP_HOME

RUN mkdir -p /opt/hadoop/dfs/data     

RUN ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa && \
    cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys && \
    chmod 0600 ~/.ssh/authorized_keys
  
COPY core-site.xml $HADOOP_HOME/etc/hadoop/core-site.xml
COPY hdfs-site.xml $HADOOP_HOME/etc/hadoop/hdfs-site.xml
COPY yarn-site.xml $HADOOP_HOME/etc/hadoop/yarn-site.xml

EXPOSE 9864

COPY entrypoint.sh /etc/entrypoint.sh

ENTRYPOINT ["sh", "/etc/entrypoint.sh"]
