#!/bin/bash -x
set(CMAKE_Fortran_COMPILER "ifx" CACHE STRING "" FORCE)
if [ -z "${LAMMPS_DIR}" ]
then
    echo "Must set LAMMPS_DIR environment variable"
    exit 1
fi

if [ -z "${LAMMPS_CI_RUNNER}" ]
then
    # local testing
    BUILD=build-$(basename $0 .sh)
else
    # when running lammps_test or inside jenkins
    BUILD=build
fi

CMAKE_COMMAND=mingw64-cmake

LAMMPS_COMPILE_NPROC=${LAMMPS_COMPILE_NPROC-8}

if [ -z "${CCACHE_DIR}" ]
then
    export CCACHE_DIR="$PWD/.ccache"
fi

if [ -z "${HTTP_CACHE_URL}" ] || [ -z "${LAMMPS_HTTP_CACHE_CONFIG}" ]
then
    BUILD_HTTP_CACHE_CONFIGURATION=""
else
    BUILD_HTTP_CACHE_CONFIGURATION="-D LAMMPS_DOWNLOADS_URL=${HTTP_CACHE_URL} -C ${LAMMPS_HTTP_CACHE_CONFIG}"
fi

# Set up environment
ccache -M 10G

# Create build directory
if [ -d "${BUILD}" ]; then
    rm -rf ${BUILD}
fi

mkdir -p ${BUILD}
cd ${BUILD}

# Configure
${CMAKE_COMMAND} \
      ${BUILD_HTTP_CACHE_CONFIGURATION} \
      -C ${LAMMPS_DIR}/cmake/presets/mingw-cross.cmake \
      -D DOWNLOAD_POTENTIALS=off \
      -D CMAKE_CXX_COMPILER_LAUNCHER=ccache \
      -D CMAKE_BUILD_TYPE="Release" \
      -D CMAKE_TUNE_FLAGS="-Wall -Wextra -Wno-unused-return-value -Wno-maybe-uninitialized" \
      -D BUILD_MPI=on \
      -D BUILD_OMP=on \
      -D BUILD_SHARED_LIBS=on \
      -D LAMMPS_SIZES=SMALLBIG \
      -D LAMMPS_EXCEPTIONS=on \
      ${LAMMPS_DIR}/cmake || exit 1

# Build
cmake --build . -- -j ${LAMMPS_COMPILE_NPROC} || exit 1

ccache -s
