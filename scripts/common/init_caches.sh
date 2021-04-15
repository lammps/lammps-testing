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

echo "##############################################################################"
echo "Initializing LAMMPS offline compilation environment"
echo "##############################################################################"

echo "Using $LAMMPS_CACHING_DIR as cache directory..."

SCRIPT_DIR="$(dirname "$(realpath "$0")")"
SCRIPT_BASE_DIR=$LAMMPS_TESTING_DIR/scripts
COMMON_SCRIPTS_DIR=${SCRIPT_BASE_DIR}/common

export GITHUB_PROXY_DIR=$LAMMPS_CACHING_DIR/github
export LOGGING_DIR=$LAMMPS_CACHING_DIR/logs
export PIP_CACHE_DIR=$LAMMPS_CACHING_DIR/pip
export HTTP_CACHE_DIR=$LAMMPS_CACHING_DIR/http

mkdir -p $GITHUB_PROXY_DIR
mkdir -p $LOGGING_DIR
mkdir -p $PIP_CACHE_DIR
mkdir -p $HTTP_CACHE_DIR

${COMMON_SCRIPTS_DIR}/init_pip_cache.sh
${COMMON_SCRIPTS_DIR}/init_git_cache.sh
${COMMON_SCRIPTS_DIR}/init_http_cache.sh  
echo "##############################################################################"
echo
echo "To activate:"
echo "source ${COMMON_SCRIPTS_DIR}/use_caches.sh"
echo
echo "##############################################################################"
