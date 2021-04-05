#!/bin/bash

if [ -z "${HTTP_PROXY_DIR}" ]
then
    echo "Must set HTTP_PROXY_DIR environment variable"
    exit 1
fi

if [ -z "${HTTP_PROXY_PORT}" ]
then
    HTTP_PROXY_PORT=8080
fi

python3 -m http.server $HTTP_PROXY_PORT --directory $HTTP_PROXY_DIR &
export HTTP_PROXY_PID=$!

export HTTP_PROXY_URL=http://localhost:$HTTP_PROXY_PORT
