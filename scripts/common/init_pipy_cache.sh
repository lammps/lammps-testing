#!/bin/bash

devpi-init
devpi-server &

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
