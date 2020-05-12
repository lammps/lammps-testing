#!/bin/bash
export WORKING_DIR=$PWD
SCRIPTDIR="$(dirname "$(realpath "$0")")"

# copy tests
rsync -a --delete $LAMMPS_TESTING_DIR/tests .

source pyenv/bin/activate

export LD_LIBRARY_PATH=$VIRTUAL_ENV/lib64:$VIRTUAL_ENV/lib:$LD_LIBRARY_PATH
export LAMMPS_BINARY=${VIRTUAL_ENV}/bin/lmp
export LAMMPS_POTENTIALS="${VIRTUAL_ENV}/share/lammps/potentials"
export LC_ALL=C.UTF-8

rm *.xml || true

nosetests -v --with-xunit --xunit-file=regression_01.xml tests/test_regression.py

deactivate
