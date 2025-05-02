#!/bin/bash

set -e

inotifywait -m -r -e close_write --format '%w%f' "$LOG_SCRIPT_DIR" | while read -r FILE_DIR; do
    if [ -f "$FILE_DIR" ]; then
        APP_DIR="${FILE_DIR%/*/*}"
        chown -R "${UID}:${GID}" "$APP_DIR"
        echo "[INFO] Got permission to: $APP_DIR"
    fi
done