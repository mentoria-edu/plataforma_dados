#!/bin/bash
set -e

NAMENODE_PORT=9000
MAX_ATTEMPTS=10
WAIT_SECONDS=5


log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

wait_for_port() {
    local port=$1
    local max_attempts=$2
    local wait_seconds=$3
    local attempt=1
    while [ $attempt -le $max_attempts ]; do
        if netstat -tlnp 2>/dev/null | grep -q ":$port"; then
            return 0
        fi
        log "Attempt $attempt/$max_attempts - Port $port not ready..."
        attempt=$((attempt + 1))
        sleep "$wait_seconds"
    done
    return 1
}

wait_for_namenode_process() {
    local max_attempts=$1
    local wait_seconds=$2
    local attempt=1
    while [ $attempt -le $max_attempts ]; do
        if pgrep -f "proc_namenode" >/dev/null; then
            return 0
        fi
        log "Attempt $attempt/$max_attempts - NameNode process not running..."
        attempt=$((attempt + 1))
        sleep "$wait_seconds"
    done
    return 1
}

wait_for_safemode_exit() {
    local max_attempts=$1
    local wait_seconds=$2
    local attempt=1
    while [ $attempt -le $max_attempts ]; do
        if hdfs dfsadmin -safemode get | grep -q "Safe mode is OFF"; then
            return 0
        fi
        log "Attempt $attempt/$max_attempts - Still in safe mode..."
        hdfs dfsadmin -safemode leave || true
        attempt=$((attempt + 1))
        sleep "$wait_seconds"
    done
    return 1
}


if [ ! -f "$HDFS_VERSION" ]; then
    log "Formatting NameNode for the first time..."
    hdfs namenode -format -force
fi

log "Starting HDFS NameNode..."
hdfs --daemon start namenode

log "Waiting for NameNode to start..."
if ! wait_for_namenode_process $MAX_ATTEMPTS $WAIT_SECONDS; then
    log "ERROR: NameNode process did not start!"
    tail -20 "$HADOOP_HOME"/logs/hadoop-*-namenode-*.log || true
    exit 1
fi

log "Waiting for port $NAMENODE_PORT..."
if ! wait_for_port $NAMENODE_PORT $MAX_ATTEMPTS $WAIT_SECONDS; then
    log "ERROR: NameNode is not listening on port $NAMENODE_PORT!"
    netstat -tlnp || true
    exit 1
fi

log "Waiting for HDFS to exit safe mode..."
if ! wait_for_safemode_exit $MAX_ATTEMPTS $WAIT_SECONDS; then
    log "ERROR: HDFS did not exit safe mode!"
    exit 1
fi

log "Creating HDFS directories..."
hadoop fs -mkdir -p /spark_events
hadoop fs -mkdir -p /lakehouse
hadoop fs -mkdir -p /yarn_logs
hadoop fs -mkdir -p /spark_events_log

log "NameNode is up and ready!"
