#!/bin/bash -x
CMAKE_COMMAND=mingw32-cmake

LAMMPS_COMPILE_NPROC=8
LAMMPS_CXX_COMPILER_FLAGS="-Wall -Wno-maybe-uninitialized"
LAMMPS_C_COMPILER_FLAGS="-Wall -Wno-maybe-uninitialized"

export CCACHE_DIR="$PWD/.ccache"

# Set up environment
ccache -M 5G

# Configure
${CMAKE_COMMAND} -C ${LAMMPS_DIR}/cmake/presets/mingw-cross.cmake \
      -D CMAKE_CXX_FLAGS="${LAMMPS_CXX_COMPILER_FLAGS}" \
      -D CMAKE_C_FLAGS="${LAMMPS_C_COMPILER_FLAGS}" \
      -D BUILD_MPI=off \
      -D BUILD_OMP=off \
      -D BUILD_SHARED_LIBS=off \
      -D LAMMPS_SIZES=SMALLSMALL \
      -D LAMMPS_EXCEPTIONS=off \
      ${LAMMPS_DIR}/cmake || exit 1

# Build
make -j ${LAMMPS_COMPILE_NPROC} || exit 1

ccache -s
