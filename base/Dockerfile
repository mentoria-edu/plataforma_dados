FROM eclipse-temurin:8-jdk-jammy

ARG BASE_DIR_PATH="/opt"

ARG HADOOP_VERSION="3.3.6"
ARG HIVE_VERSION="3.1.3"
ARG SPARK_VERSION="3.5.5"
ARG JAR_POSTGRES_VERSION="42.7.5"
ARG USER_HDFS="root"
ARG FOLDER_COMMON_FILES="./common"
ARG CLIENT_NODE="false"
ARG SPECIFIC_NODE="master"
ARG FOLDER_COMMON_FILES="./common"
ARG FOLDER_SCRIPTS_FILES="./scripts"

ARG LINK_DOWNLOAD_HADOOP="https://dlcdn.apache.org/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz"
ARG LINK_DOWNLOAD_SPARK="https://dlcdn.apache.org/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop3.tgz"
ARG LINK_DOWNLOAD_HIVE="https://archive.apache.org/dist/hive/hive-${HIVE_VERSION}/apache-hive-${HIVE_VERSION}-bin.tar.gz"
ARG LINK_JAR_POSTGRES="https://repo1.maven.org/maven2/org/postgresql/postgresql/${JAR_POSTGRES_VERSION}/postgresql-${JAR_POSTGRES_VERSION}.jar"

ENV SPECIFIC_NODE=${SPECIFIC_NODE}
ENV CLIENT_NODE=${CLIENT_NODE}

ENV GENERAL_CONFIGS="${BASE_DIR_PATH}/config"
ENV GENERAL_SCRIPTS="${BASE_DIR_PATH}/scripts"

ENV HADOOP_HOME="${BASE_DIR_PATH}/hadoop"
ENV SPARK_HOME="${BASE_DIR_PATH}/spark"
ENV HIVE_HOME="${BASE_DIR_PATH}/hive"

ENV HADOOP_CONF_DIR="${BASE_DIR_PATH}/hadoop/etc/hadoop"
ENV HADOOP_BIN_DIR="${HADOOP_HOME}/bin"
ENV YARN_CONF_DIR="${HADOOP_CONF_DIR}"
ENV YARN_CONTAINER_RUNTIME_DOCKER_MOUNTS="/logs:/tmp/logs:rw"

ENV SPARK_CONF_DIR="${SPARK_HOME}/conf"
ENV SPARK_SBIN_DIR="${SPARK_HOME}/sbin"
ENV SPARK_BIN_DIR="${SPARK_HOME}/bin"
ENV SPARK_PYTHON_EXAMPLES="${SPARK_HOME}/examples/src/main/python"
ENV SPARK_EVENTS_DIR="${SPARK_HOME}/spark-events"

ENV VERSION_HDFS="${HADOOP_HOME}/dfs/name/current/VERSION"
ENV HDFS_NAMENODE_USER="${USER_HDFS}"
ENV HDFS_DATANODE_USER="${USER_HDFS}"
ENV HDFS_SECONDARYNAMENODE_USER="${USER_HDFS}"

ENV HADOOP_TAR_GZ_FILE="${HADOOP_HOME}/hadoop-${HADOOP_VERSION}.tar.gz"
ENV SPARK_TAR_GZ_FILE="${SPARK_HOME}/spark-${SPARK_VERSION}-bin-hadoop3.tgz"
ENV HIVE_TAR_GZ_FILE="${HIVE_HOME}/apache-hive-${HIVE_VERSION}-bin.tar.gz"

ENV PATH=$PATH:"$HIVE_HOME/bin"
ENV PATH=$PATH:"$HADOOP_HOME/bin:$HADOOP_HOME/sbin"

RUN apt update && \ 
    apt install -y --no-install-recommends \  
    wget \    
    openssh-client \
    openssh-server \
    python3 \
    rsync \
    wget \
    ssh \
    tini \
    krb5-user \
    libnss3  \
    net-tools \
    inotify-tools    

# RUN wget http://security.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2.24_amd64.deb && \
#     dpkg -i libssl1.1_1.1.1f-1ubuntu2.24_amd64.deb && \
#     rm libssl1.1_1.1.1f-1ubuntu2.24_amd64.deb    

RUN mkdir -p ${HADOOP_HOME} && \
    mkdir -p ${SPARK_HOME} && \
    mkdir -p ${HIVE_HOME} && \
    wget ${LINK_DOWNLOAD_HADOOP} -O ${HADOOP_TAR_GZ_FILE} && \
    wget ${LINK_DOWNLOAD_SPARK} -O ${SPARK_TAR_GZ_FILE} && \
    wget ${LINK_DOWNLOAD_HIVE} -O ${HIVE_TAR_GZ_FILE} && \
    wget ${LINK_JAR_POSTGRES} && \
    tar -xvzf ${HADOOP_TAR_GZ_FILE} -C ${HADOOP_HOME} --strip-components=1 &&\
    tar -xvzf ${SPARK_TAR_GZ_FILE} -C ${SPARK_HOME} --strip-components=1 && \
    tar -xvzf ${HIVE_TAR_GZ_FILE} -C ${HIVE_HOME} --strip-components=1 && \
    mv postgresql-${JAR_POSTGRES_VERSION}.jar ${HIVE_HOME}/lib && \ 
    rm ${HADOOP_TAR_GZ_FILE} && \
    rm ${SPARK_TAR_GZ_FILE} && \
    rm ${HIVE_TAR_GZ_FILE}

RUN mkdir -p ${GENERAL_CONFIGS} && \
    mkdir -p ${GENERAL_SCRIPTS} && \
    mkdir -p ${HADOOP_HOME}/dfs/data && \
    mkdir -p ${HADOOP_HOME}/dfs/name && \  
    mkdir -p /tmp/logs && \
    mkdir -p /tmp/dir && \
    mkdir -p /tmp/spark && \
    mkdir -p ${HADOOP_HOME}/logs

RUN echo "export JAVA_HOME=${JAVA_HOME}" >> $HADOOP_HOME/etc/hadoop/hadoop-env.sh && \
    echo 'export HADOOP_HOME=$HADOOP_HOME' >> $HIVE_HOME/bin/hive_config.sh

RUN ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa && \
    cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys && \
    chmod 0600 ~/.ssh/authorized_keys

COPY ${FOLDER_COMMON_FILES}/* ${GENERAL_CONFIGS}
COPY ${FOLDER_SCRIPTS_FILES}/* ${GENERAL_SCRIPTS}

RUN cp ${GENERAL_CONFIGS}/* ${HADOOP_CONF_DIR}/ && \
    cp ${GENERAL_CONFIGS}/* ${SPARK_CONF_DIR}/ && \
    cp ${GENERAL_SCRIPTS}/* ${SPARK_CONF_DIR}/ && \
    cp ${GENERAL_SCRIPTS}/logs_yarn.sh ${HADOOP_BIN_DIR}/ && \
    rm -r ${GENERAL_CONFIGS} && \
    rm -r ${GENERAL_SCRIPTS}

COPY ./entrypoint.sh ${BASE_DIR_PATH}/entrypoint.sh
ENTRYPOINT ["bash", "-c", "bash /opt/entrypoint.sh"]