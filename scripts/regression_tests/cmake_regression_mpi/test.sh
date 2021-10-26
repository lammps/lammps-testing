#!/bin/bash
export WORKING_DIR=$PWD
SCRIPT_BASE_DIR=$LAMMPS_TESTING_DIR/scripts
SCRIPTDIR="$(dirname "$(realpath "$0")")"
export PYTHON=$(which python3)

# copy tests
rsync -a --delete $LAMMPS_TESTING_DIR/tests .

source pyenv/bin/activate

export LD_LIBRARY_PATH=$VIRTUAL_ENV/lib64:$VIRTUAL_ENV/lib:$LD_LIBRARY_PATH
export LAMMPS_BINARY=${VIRTUAL_ENV}/bin/lmp
export LAMMPS_POTENTIALS="${VIRTUAL_ENV}/share/lammps/potentials"
export LC_ALL=C.UTF-8

rm *.xml || true

nosetests -v --with-xunit --xunit-file=regression_01.xml tests/test_long_range_electrostatics.py
nosetests -v --with-xunit --xunit-file=regression_02.xml tests/test_regression.py
# run single test case
#nosetests -v -s --with-xunit --xunit-file=regression_02.xml tests/test_regression.py:BodyTestCase


deactivate
