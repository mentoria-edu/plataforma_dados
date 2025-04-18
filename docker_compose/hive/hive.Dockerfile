FROM ubuntu:22.04

ARG V_HADOOP=3.3.6
ARG V_HIVE=4.0.1
ARG V_JAVA=8

ENV HIVE_HOME=/opt/hive
ENV PATH=$PATH:$HIVE_HOME/bin
ENV JAVA_VERSION=$V_JAVA
ENV JAVA_HOME=/usr/lib/jvm/java-$JAVA_VERSION-openjdk-amd64
ENV HADOOP_HOME=/opt/hadoop
ENV USER_HIVE=hive
ENV USER_HOME=/home/$USER_HIVE

RUN adduser --gecos "" --disabled-password $USER_HIVE && \
    usermod -aG sudo $USER_HIVE && \
    chown -R $USER_HIVE:$USER_HIVE ${USER_HOME} 

RUN echo 'export PATH=$PATH:$HIVE_HOME/bin' >> $USER_HOME/.bashrc

RUN apt update && apt install -y \
    openjdk-$JAVA_VERSION-jdk \
    wget 

RUN wget https://dlcdn.apache.org/hadoop/common/hadoop-${V_HADOOP}/hadoop-${V_HADOOP}.tar.gz && \
    tar -xvzf hadoop-${V_HADOOP}.tar.gz -C /opt && \
    mv /opt/hadoop-${V_HADOOP} $HADOOP_HOME

RUN wget https://dlcdn.apache.org/hive/hive-${V_HIVE}/apache-hive-${V_HIVE}-bin.tar.gz && \
    tar -xvzf apache-hive-${V_HIVE}-bin.tar.gz -C /opt && \
    mv /opt/apache-hive-${V_HIVE}-bin $HIVE_HOME

RUN echo 'export HADOOP_HOME=$HADOOP_HOME' >> $HIVE_HOME/bin/hive_config.sh   

RUN chown -R $USER_HIVE:$USER_HIVE $HIVE_HOME

COPY hive-site.xml $HIVE_HOME/conf

EXPOSE 9083

COPY entrypoint.sh /etc/entrypoint.sh

ENTRYPOINT ["sh", "/etc/entrypoint.sh"]
