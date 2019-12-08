#!/bin/bash

if [ -z "$LAMMPS_MPI_MODE=" ]
then
    export LAMMPS_MPI_MODE="openmpi"
fi

if [ -z "$LAMMPS_TEST_MODES=" ]
then
    export LAMMPS_TEST_MODES="serial"
fi

source ${LAMMPS_BUILD_DIR}/pyenv/bin/activate
pip install nose
pip install git+https://github.com/gcovr/gcovr.git

export LD_LIBRARY_PATH=$VIRTUAL_ENV/lib64:$VIRTUAL_ENV/lib:$LD_LIBRARY_PATH
echo "-------------------------------------------------------------------------------------"
env | grep LAMMPS_
echo "-------------------------------------------------------------------------------------"

export LAMMPS_BINARY=${VIRTUAL_ENV}/bin/lmp
export LAMMPS_POTENTIALS="${VIRTUAL_ENV}/share/lammps/potentials"
cd ../..
lammps_run_tests --processes 8 tests/test_commands.py tests/test_examples.py
cd ..

make gen_coverage_xml

deactivate
