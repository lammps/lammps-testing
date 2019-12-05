#!/bin/bash
export CCACHE_DIR="$PWD/.ccache"

# Configure
if [ -z "$CC" ]
then
    export CC=gcc
fi

if [ -z "$CXX" ]
then
    export CXX=g++
fi

if [ -z "$CMAKE_OPTIONS" ]
then
    export CMAKE_OPTIONS=""
fi

if [ -z "$LAMMPS_MPI_MODE=" ]
then
    export LAMMPS_MPI_MODE="openmpi"
fi

if [ -z "$LAMMPS_TEST_MODES=" ]
then
    export LAMMPS_TEST_MODES="serial"
fi

ccache -M 5G

virtualenv --python=$(which python3) pyenv

source pyenv/bin/activate
pip install nose
pip install git+https://github.com/gcovr/gcovr.git

set -x
cmake ${CMAKE_OPTIONS[@]} -D CMAKE_INSTALL_PREFIX=${VIRTUAL_ENV} ${LAMMPS_DIR}/cmake

# Build
make -j ${LAMMPS_COMPILE_NPROC}
make install

export LD_LIBRARY_PATH=$VIRTUAL_ENV/lib64:$VIRTUAL_ENV/lib:$LD_LIBRARY_PATH
echo "-------------------------------------------------------------------------------------"
env | grep LAMMPS_
echo "-------------------------------------------------------------------------------------"

export LAMMPS_BINARY=${VIRTUAL_ENV}/bin/lmp
export LAMMPS_POTENTIALS="${VIRTUAL_ENV}/share/lammps/potentials"
cd ../..
python run_tests.py --processes 8 tests/test_commands.py tests/test_examples.py
cd ..

make gen_coverage_xml

deactivate
ccache -s
