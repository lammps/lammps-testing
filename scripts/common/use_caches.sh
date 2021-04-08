#!/bin/bash

if [ -z "${LAMMPS_TESTING_DIR}" ]
then
    echo "Must set LAMMPS_TESTING_DIR environment variable"
    exit 1
fi

if test -n "$BASH" ; then script=$BASH_SOURCE
else script=$0
fi

SCRIPT_DIR="$(dirname "$(realpath "$script")")"
SCRIPT_BASE_DIR=$LAMMPS_TESTING_DIR/scripts
COMMON_SCRIPTS_DIR=${SCRIPT_BASE_DIR}/common

export GITHUB_PROXY_DIR=$PWD/github
export LOGGING_DIR=$PWD/logs
export PIP_CACHE_DIR=$PWD/pip
export HTTP_CACHE_DIR=$PWD/http

source ${COMMON_SCRIPTS_DIR}/use_git_cache.sh
source ${COMMON_SCRIPTS_DIR}/use_pip_cache.sh
source ${COMMON_SCRIPTS_DIR}/use_http_cache.sh  
