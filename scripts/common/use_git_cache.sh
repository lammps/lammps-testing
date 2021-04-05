#!/bin/bash
# needs to be sourced
if [ -z "${GITHUB_PROXY_DIR}" ]
then
    echo "Must set GITHUB_PROXY_DIR environment variable"
    exit 1
fi

export GIT_CONFIG_COUNT=1
export GIT_CONFIG_KEY_0=url.$GITHUB_PROXY_DIR/.insteadOf
export GIT_CONFIG_VALUE_0=git://github.com/
