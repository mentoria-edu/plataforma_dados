FROM eclipse-temurin:8-jdk-jammy

ARG SPARK_VERSION="spark-3.5.5"
ARG SPARK_FOLDER_NAME="${SPARK_VERSION}-bin-hadoop3.tgz"
ARG LINK_DOWNLOAD_SPARK="https://dlcdn.apache.org/spark/${SPARK_VERSION}/${SPARK_FOLDER_NAME}"

ENV SPARK_HOME="/opt/spark"
ENV SPARK_CONF_DIR="${SPARK_HOME}/conf/"
ENV SPARK_SBIN_DIR="${SPARK_HOME}/sbin/"
ENV HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop
ENV YARN_CONF_DIR=/opt/hadoop/etc/hadoop
ENV SPARK_BIN_DIR="${SPARK_HOME}/bin/"
ENV SPARK_PYTHON_EXAMPLES="${SPARK_HOME}/examples/src/main/python/"
ENV SPARK_EVENTS_DIR="${SPARK_HOME}/spark-events/"
ENV PATH="${SPARK_HOME}:${SPARK_SBIN_DIR}:${SPARK_BIN_DIR}:${SPARK_EVENTS_DIR}:${PATH}"

RUN apt update -y && \
    apt install -y --no-install-recommends \
    python3 \
    rsync \
    wget \
    ssh \
    tini \
    krb5-user \
    libnss3  \
    net-tools
    # net-tools && \
    # rm -rf /var/lib/apt/lists/*

RUN mkdir -p ${SPARK_HOME} && \
    mkdir -p ${SPARK_EVENTS_DIR} && \
    wget -q ${LINK_DOWNLOAD_SPARK} -O ${SPARK_HOME}/${SPARK_FOLDER_NAME} && \
    tar xzf ${SPARK_HOME}/${SPARK_FOLDER_NAME} -C ${SPARK_HOME} --strip-components=1 && \
    rm -f ${SPARK_HOME}/${SPARK_FOLDER_NAME}

RUN wget https://repo1.maven.org/maven2/org/apache/hive/hive-metastore/4.0.1/hive-metastore-4.0.1.jar && \
    wget https://repo1.maven.org/maven2/org/apache/hive/hive-common/4.0.1/hive-common-4.0.1.jar && \
    wget https://repo1.maven.org/maven2/org/apache/hive/hive-storage-api/4.0.1/hive-storage-api-4.0.1.jar && \
    wget https://repo1.maven.org/maven2/org/apache/hive/hive-serde/4.0.1/hive-serde-4.0.1.jar && \
    mv hive-metastore-4.0.1.jar ${SPARK_HOME}/jars && \
    mv hive-common-4.0.1.jar ${SPARK_HOME}/jars && \
    mv hive-storage-api-4.0.1.jar ${SPARK_HOME}/jars && \
    mv hive-serde-4.0.1.jar ${SPARK_HOME}/jars
    
COPY spark-defaults.conf ${SPARK_CONF_DIR}/spark-defaults.conf

COPY ./hive_teste_2.py ${SPARK_HOME}

CMD ["bash", "-c",  "${SPARK_HOME}/bin/spark-submit  --master yarn --deploy-mode cluster ${SPARK_HOME}/hive_teste_2.py"]