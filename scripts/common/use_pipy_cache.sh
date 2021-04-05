#!/bin/bash
# needs to be sourced
devpi-server --offline-mode &
export DEVPI_SERVER_PID=$!
export PIP_INDEX_URL=http://localhost:3141/root/pypi/+simple
