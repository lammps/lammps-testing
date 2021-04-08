#!/bin/bash

if [ -z "${LAMMPS_TESTING_DIR}" ]
then
    echo "Must set LAMMPS_TESTING_DIR environment variable"
    exit 1
fi


SCRIPT_DIR="$(dirname "$(realpath "$0")")"
SCRIPT_BASE_DIR=$LAMMPS_TESTING_DIR/scripts
COMMON_SCRIPTS_DIR=${SCRIPT_BASE_DIR}/common

export GITHUB_PROXY_DIR=$PWD/github
export LOGGING_DIR=$PWD/logs
export DEVPI_SERVER_DIR=$PWD/devpi
export HTTP_CACHE_DIR=$PWD/http

mkdir -p $GITHUB_PROXY_DIR
mkdir -p $LOGGING_DIR
mkdir -p $DEVPI_SERVER_DIR
mkdir -p $HTTP_CACHE_DIR

${COMMON_SCRIPTS_DIR}/init_pipy_cache.sh
${COMMON_SCRIPTS_DIR}/init_git_cache.sh
${COMMON_SCRIPTS_DIR}/init_http_cache.sh  
