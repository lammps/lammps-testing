#!/bin/bash
export CCACHE_DIR="$PWD/.ccache"
export CC=gcc
export CXX=g++
export OMPI_CC=$CC
export OMPI_CXX=$CXX
export PYTHON=$(which python)

# Configure

ccache -M 5G

set -x
cmake ${CMAKE_OPTIONS[@]} -D PYTHON_EXECUTABLE=$PYTHON $LAMMPS_DIR/cmake

# Build
make -j $LAMMPS_COMPILE_NPROC
ccache -s
