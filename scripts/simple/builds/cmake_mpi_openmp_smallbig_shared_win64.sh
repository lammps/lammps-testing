#!/bin/bash -x
if [ -z "${LAMMPS_DIR}" ]
then
        echo "Must set LAMMPS_DIR environment variable"
        exit 1
fi
BUILD=build-$(basename $0 .sh)

CMAKE_COMMAND=mingw64-cmake

LAMMPS_COMPILE_NPROC=${LAMMPS_COMPILE_NPROC-8}
LAMMPS_CXX_COMPILER_FLAGS="-Wall -Wno-maybe-uninitialized"
LAMMPS_C_COMPILER_FLAGS="-Wall -Wno-maybe-uninitialized"

export CCACHE_DIR="$PWD/.ccache"

# Set up environment
ccache -M 5G

# Create build directory
if [ -d "${BUILD}" ]; then
    rm -rf ${BUILD}
fi

mkdir -p ${BUILD}
cd ${BUILD}

# Configure
${CMAKE_COMMAND} -C ${LAMMPS_DIR}/cmake/presets/mingw-cross.cmake \
      -D CMAKE_CXX_COMPILER_LAUNCHER=ccache \
      -D CMAKE_CXX_FLAGS="${LAMMPS_CXX_COMPILER_FLAGS}" \
      -D CMAKE_C_FLAGS="${LAMMPS_C_COMPILER_FLAGS}" \
      -D BUILD_MPI=on \
      -D BUILD_OMP=on \
      -D BUILD_SHARED_LIBS=on \
      -D LAMMPS_SIZES=SMALLBIG \
      -D LAMMPS_EXCEPTIONS=off \
      ${LAMMPS_DIR}/cmake || exit 1

# Build
make -j ${LAMMPS_COMPILE_NPROC} || exit 1

ccache -s
