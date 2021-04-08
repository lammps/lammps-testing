#!/bin/bash
# needs to be sourced

if [ -z "${LOGGING_DIR}" ]
then
    echo "Must set LOGGING_DIR environment variable"
    exit 1
fi

if [ -z "${DEVPI_SERVER_DIR}" ]
then
    echo "Must set DEVPI_SERVER_DIR environment variable"
    exit 1
fi

devpi-server --serverdir $DEVPI_SERVER_DIR --offline-mode 2>&1 > $LOGGING_DIR/devpi_offline.log &
export DEVPI_SERVER_PID=$!
export PIP_INDEX_URL=http://localhost:3141/root/pypi/+simple
