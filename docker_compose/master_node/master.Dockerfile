FROM eclipse-temurin:8-jdk-jammy

ARG V_HADOOP=3.4.1
ARG V_HIVE=4.0.1
ARG V_SPARK=3.5.5

ENV HADOOP_HOME=/opt/hadoop
ENV HIVE_HOME=/opt/hive
ENV SPARK_HOME=/opt/spark
ENV PATH=$PATH:$HIVE_HOME/bin
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
ENV HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop
ENV YARN_CONF_DIR=/opt/hadoop/etc/hadoop
ENV USER_HDFS=root
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

RUN wget https://dlcdn.apache.org/hive/hive-${V_HIVE}/apache-hive-${V_HIVE}-bin.tar.gz && \
    tar -xvzf apache-hive-${V_HIVE}-bin.tar.gz -C /opt && \
    mv /opt/apache-hive-${V_HIVE}-bin $HIVE_HOME   
    
RUN wget https://dlcdn.apache.org/spark/spark-${V_SPARK}/spark-${V_SPARK}-bin-hadoop3.tgz && \         
    tar -xvzf spark-${V_SPARK}-bin-hadoop3.tgz -C /opt && \
    mv /opt/spark-${V_SPARK}-bin-hadoop3 $SPARK_HOME

RUN wget https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.5/postgresql-42.7.5.jar && \
    mv postgresql-42.7.5.jar ${HIVE_HOME}/lib

RUN echo "export JAVA_HOME=${JAVA_HOME}" >> $HADOOP_HOME/etc/hadoop/hadoop-env.sh && \
    echo 'export HADOOP_HOME=$HADOOP_HOME' >> $HIVE_HOME/bin/hive_config.sh 

#RUN adduser --gecos "" --disabled-password $USER_HDFS && \
#    usermod -aG sudo $USER_HDFS && \
#    chown -R $USER_HDFS:$USER_HDFS ${USER_HOME} && \
#    adduser --gecos "" --disabled-password hive 

#RUN chown -R $USER_HDFS:$USER_HDFS $HADOOP_HOME

RUN ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa && \
    cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys && \
    chmod 0600 ~/.ssh/authorized_keys

RUN mkdir -p /opt/hadoop/dfs/name 
  
COPY core-site.xml $HADOOP_HOME/etc/hadoop/core-site.xml
COPY hdfs-site.xml $HADOOP_HOME/etc/hadoop/hdfs-site.xml
COPY yarn-site.xml $HADOOP_HOME/etc/hadoop/yarn-site.xml
COPY hive-site.xml $HIVE_HOME/conf

RUN hdfs namenode -format  

#RUN schematool -dbType postgres -initSchema

EXPOSE 9870 1000 8088

COPY entrypoint.sh /etc/entrypoint.sh

ENTRYPOINT ["sh", "/etc/entrypoint.sh"]
