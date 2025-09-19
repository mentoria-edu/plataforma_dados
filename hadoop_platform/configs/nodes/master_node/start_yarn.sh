#!/bin/bash
set -e

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

log "Starting YARN ResourceManager..."
yarn --daemon start resourcemanager

log "Hadoop environment initialized successfully!"
