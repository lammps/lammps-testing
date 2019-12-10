#!/bin/bash
if [ -z "$LAMMPS_MPI_MODE=" ]
then
    export LAMMPS_MPI_MODE="openmpi"
fi

if [ -z "$LAMMPS_TEST_MODES=" ]
then
    export LAMMPS_TEST_MODES="serial"
fi

if [ -z "$LAMMPS_TESTING_NPROC=" ]
then
    export LAMMPS_TESTING_NPROC=8
fi

# copy tests
rsync -a $LAMMPS_TESTING_DIR/tests .

source $LAMMPS_BUILD_DIR/pyenv/bin/activate

# install lammps-testing package
cd $LAMMPS_TESTING_DIR
python setup.py install


export LD_LIBRARY_PATH=$VIRTUAL_ENV/lib64:$VIRTUAL_ENV/lib:$LD_LIBRARY_PATH
export LAMMPS_BINARY=${VIRTUAL_ENV}/bin/lmp
export LAMMPS_POTENTIALS="${VIRTUAL_ENV}/share/lammps/potentials"

deactivate
cd $WORKING_DIR
