#!/bin/bash
export CCACHE_DIR="$PWD/.ccache"
export PYTHON=$(which python3)

if [ -z "$CC" ]
then
    export CC=gcc
fi

if [ -z "$CXX" ]
then
    export CXX=g++
fi

# Configure

ccache -M 5G

virtualenv --python=$PYTHON pyenv

source pyenv/bin/activate

git -C ${LAMMPS_DIR} checkout ${LAMMPS_COMMIT}
git -C ${LAMMPS_DIR} rev-parse HEAD > COMMIT

set -x

cmake -C ${LAMMPS_DIR}/cmake/presets/all_off.cmake \
      -D CXX_COMPILER_LAUNCHER=ccache \
      -D CMAKE_CXX_FLAGS="${LAMMPS_CXX_COMPILER_FLAGS}" \
      -D CMAKE_C_FLAGS="${LAMMPS_C_COMPILER_FLAGS}" \
      -D CMAKE_C_COMPILER="$CC" \
      -D CMAKE_CXX_COMPILER="$CXX" \
      -D CMAKE_INSTALL_PREFIX=${VIRTUAL_ENV} \
      ${LAMMPS_CMAKE_OPTIONS} \
      ${LAMMPS_DIR}/cmake

# Build
make -j ${LAMMPS_COMPILE_NPROC}
make install

deactivate

ccache -s

export LAMMPS_BUILD_DIR=$PWD
