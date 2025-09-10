#!/bin/bash
set -e

METASTORE_PORT=9083
METASTORE_MAX_ATTEMPTS=30
METASTORE_WAIT_SECONDS=5

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

log "Configuring Hive Metastore schema..."
schematool -dbType postgres -info || {
    log "Schema not found, initializing..."
    schematool -dbType postgres -initSchema
}

log "Validating and upgrading schema if needed..."
schematool -dbType postgres -validate || {
    log "Schema validation failed, upgrading..."
    schematool -dbType postgres -upgradeSchema
}

log "Starting Hive Metastore service..."
hive --service metastore > "$HADOOP_HOME/logs/metastore.log" 2>&1 &
METASTORE_PID=$!

log "Waiting for Hive Metastore port $METASTORE_PORT..."
if ! wait_for_port $METASTORE_PORT $METASTORE_MAX_ATTEMPTS $METASTORE_WAIT_SECONDS; then
    log "ERROR: Hive Metastore port not available!"
    if [ -f "$HADOOP_HOME/logs/metastore.log" ]; then
        log "Metastore logs:"
        cat "$HADOOP_HOME/logs/metastore.log"
    fi
    kill $METASTORE_PID 2>/dev/null || true
    exit 1
fi

log "Hive Metastore port is ready!"

log "Hive Metastore is ready and listening on port $METASTORE_PORT!"

log "Creating bronze schema in metastore..."

if ! hive -e "CREATE SCHEMA IF NOT EXISTS BRONZE;"; then
    log "ERRO: Falha ao criar o schema BRONZE via Hive CLI!"
    exit 1
fi

log "Hive Metastore initialization completed successfully!"
log "Metastore PID: $METASTORE_PID"
