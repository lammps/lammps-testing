#!/bin/bash -x
CMAKE_COMMAND=mingw64-cmake

LAMMPS_COMPILE_NPROC=${LAMMPS_COMPILE_NPROC-8}
LAMMPS_CXX_COMPILER_FLAGS="-Wall -Wno-maybe-uninitialized"
LAMMPS_C_COMPILER_FLAGS="-Wall -Wno-maybe-uninitialized"

export CCACHE_DIR="$PWD/.ccache"

# Set up environment
ccache -M 5G

# Create build directory
if [ -d "build" ]; then
    rm -rf build
fi

mkdir -p build
cd build

# Configure
${CMAKE_COMMAND} -C ${LAMMPS_DIR}/cmake/presets/mingw-cross.cmake \
      -D CXX_COMPILER_LAUNCHER=ccache \
      -D CMAKE_CXX_FLAGS="${LAMMPS_CXX_COMPILER_FLAGS}" \
      -D CMAKE_C_FLAGS="${LAMMPS_C_COMPILER_FLAGS}" \
      -D BUILD_MPI=on \
      -D BUILD_OMP=on \
      -D BUILD_SHARED_LIBS=on \
      -D LAMMPS_SIZES=SMALLBIG \
      -D LAMMPS_EXCEPTIONS=on \
      ${LAMMPS_DIR}/cmake || exit 1

# Build
make -j ${LAMMPS_COMPILE_NPROC} || exit 1

ccache -s
