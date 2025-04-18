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
    net-tools && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p ${SPARK_HOME} && \
    mkdir -p ${SPARK_EVENTS_DIR} && \
    wget -q ${LINK_DOWNLOAD_SPARK} -O ${SPARK_HOME}/${SPARK_FOLDER_NAME} && \
    tar xzf ${SPARK_HOME}/${SPARK_FOLDER_NAME} -C ${SPARK_HOME} --strip-components=1 && \
    rm -f ${SPARK_HOME}/${SPARK_FOLDER_NAME}
    
COPY spark-defaults.conf ${SPARK_CONF_DIR}/spark-defaults.conf

COPY ./teste.py ${SPARK_HOME}

CMD ["bash", "-c",  "${SPARK_HOME}/bin/spark-submit  --master yarn --deploy-mode cluster ${SPARK_HOME}/teste.py"]