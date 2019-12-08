#!/bin/bash
export CCACHE_DIR="$PWD/.ccache"
export CC=gcc
export CXX=g++
export OMPI_CC=$CC
export OMPI_CXX=$CXX
export PYTHON=$(which python3)

# Configure

ccache -M 5G

virtualenv --python=$PYTHON pyenv

source pyenv/bin/activate

cmake ${CMAKE_OPTIONS[@]} -D CMAKE_INSTALL_PREFIX=${VIRTUAL_ENV} $LAMMPS_DIR/cmake

# Build
make -j $LAMMPS_COMPILE_NPROC
make install

deactivate

ccache -s

export LAMMPS_BUILD_DIR=$PWD
