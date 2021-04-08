#!/bin/bash


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

set -x

devpi-init --serverdir ${DEVPI_SERVER_DIR} --role standalone # 2>&1 > $LOGGING_DIR/devpi_init.log
devpi-server --serverdir ${DEVPI_SERVER_DIR} & # 2>&1 > $LOGGING_DIR/devpi.log &

DEVPI_SERVER_PID=$!

# init cache
TMPENV=/tmp/initcacheenv

python3 -m venv $TMPENV
source $TMPENV/bin/activate
export PIP_INDEX_URL=http://localhost:3141/root/pypi/+simple

# install packages that might be needed
pip install --upgrade pip setuptools wheel
pip install -r $LAMMPS_DIR/doc/utils/requirements.txt
pip install -r $LAMMPS_TESTING_DIR/requirements.txt
deactivate

rm -rf $TMPENV
kill $DEVPI_SERVER_PID

# afterwards you can use devpi-server --offline-mode
# and set PIP_INDEX_URL again to use cached packages
