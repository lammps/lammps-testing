#!/bin/bash
export WORKING_DIR=$PWD
SCRIPTDIR="$(dirname "$(realpath "$0")")"

# copy tests
rsync -a --delete $LAMMPS_TESTING_DIR/tests .

source pyenv/bin/activate




# run tests
export LD_LIBRARY_PATH=$VIRTUAL_ENV/lib64:$VIRTUAL_ENV/lib:$LD_LIBRARY_PATH
export LAMMPS_BINARY=${VIRTUAL_ENV}/bin/lmp
export LAMMPS_POTENTIALS="${VIRTUAL_ENV}/share/lammps/potentials"
export LAMMPS_MPI_MODE="openmpi"
export LAMMPS_TEST_MODES="omp"
export LAMMPS_TESTING_NPROC=2

if [ "$HOSTNAME" = atlas2 ]; then
    taskset -pc 1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31 $$
fi

lammps_run_tests --processes ${LAMMPS_TESTING_NPROC} tests/test_commands.py tests/test_examples.py

#gcovr -s -x -r ${LAMMPS_DIR}/src --object-directory=${PWD}/build -o build/coverage.xml

deactivate
