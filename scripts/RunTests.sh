#!/bin/bash
SCRIPTDIR="$(dirname "$(realpath "$0")")"
export WORKING_DIR=$PWD

. $SCRIPTDIR/LAMMPSTesting.sh

source $LAMMPS_BUILD_DIR/pyenv/bin/activate
lammps_run_tests --processes ${LAMMPS_TESTING_NPROC} ${LAMMPS_TESTS}

deactivate
