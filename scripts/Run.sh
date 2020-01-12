#!/bin/bash
SCRIPTDIR="$(dirname "$(realpath "$0")")"
export WORKING_DIR=$PWD

source $LAMMPS_BUILD_DIR/pyenv/bin/activate

export LD_LIBRARY_PATH=$VIRTUAL_ENV/lib64:$VIRTUAL_ENV/lib:$LD_LIBRARY_PATH
export LAMMPS_BINARY=${VIRTUAL_ENV}/bin/lmp
export LAMMPS_POTENTIALS="${VIRTUAL_ENV}/share/lammps/potentials"

$LAMMPS_BINARY $@

deactivate
