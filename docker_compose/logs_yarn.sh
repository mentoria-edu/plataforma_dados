#!/bin/bash

set -e 

YARN_LOG_DIR="/tmp/logs"
HDFS_LOG_DIR="/yarn_logs"

inotifywait -m -r -e create --format '%w%f' "$YARN_LOG_DIR" | while read -r arquivo; do
    if [ -f "$arquivo" ]; then

        chown -R ${UID}:${GID} /tmp/logs/$arquivo

        echo "[INFO] Got permission to: $arquivo"
    fi
done