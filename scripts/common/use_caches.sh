#!/bin/bash

if [ -z "${LAMMPS_TESTING_DIR}" ]
then
    echo "Must set LAMMPS_TESTING_DIR environment variable"
    exit 1
fi

if [ -z "${LAMMPS_CACHING_DIR}" ]
then
    export LAMMPS_CACHING_DIR=$PWD
fi

if test -n "$BASH" ; then script=$BASH_SOURCE
else script=$0
fi

SCRIPT_DIR="$(dirname "$(realpath "$script")")"
SCRIPT_BASE_DIR=$LAMMPS_TESTING_DIR/scripts
COMMON_SCRIPTS_DIR=${SCRIPT_BASE_DIR}/common

export GITHUB_PROXY_DIR=$LAMMPS_CACHING_DIR/github
export LOGGING_DIR=$LAMMPS_CACHING_DIR/logs
export PIP_CACHE_DIR=$LAMMPS_CACHING_DIR/pip
export HTTP_CACHE_DIR=$LAMMPS_CACHING_DIR/http

if [ ! -d $GITHUB_PROXY_DIR ]
then
    echo "GitHub proxy directory missing"
    return
fi

if [ ! -d $LOGGING_DIR ]
then
    echo "Logging directory missing"
    return
fi

if [ ! -d $PIP_CACHE_DIR ]
then
    echo "pip cache directory missing"
    return
fi

if [ ! -d $HTTP_CACHE_DIR ]
then
    echo "HTTP cache directory missing"
    return
fi

source ${COMMON_SCRIPTS_DIR}/use_git_cache.sh
source ${COMMON_SCRIPTS_DIR}/use_pip_cache.sh
source ${COMMON_SCRIPTS_DIR}/use_http_cache.sh  

function deactivate_caches {
    deactivate_http_cache
    deactivate_pip_cache
    deactivate_git_cache
    unset -f deactivate_http_cache
    unset -f deactivate_pip_cache
    unset -f deactivate_git_cache
}
