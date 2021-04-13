#!/bin/bash -x
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

exists()
{
  command -v "$1" >/dev/null 2>&1
}

if exists "cmake3"
then
    CMAKE_COMMAND=cmake3
else
    CMAKE_COMMAND=cmake
fi

LAMMPS_COMPILE_NPROC=${LAMMPS_COMPILE_NPROC-8}

if [ -z "${CCACHE_DIR}" ]
then
    export CCACHE_DIR="$PWD/.ccache"
fi

if [ -z "${HTTP_CACHE_URL}" || -z "${LAMMPS_HTTP_CACHE_CONFIG}" ]
then
    BUILD_HTTP_CACHE_CONFIGURATION=""
else
    BUILD_HTTP_CACHE_CONFIGURATION="-D LAMMPS_DOWNLOADS_URL=${HTTP_CACHE_URL} -C ${LAMMPS_HTTP_CACHE_CONFIG}"
fi

export PYTHON=$(which python3)

# Set up environment
ccache -M 10G
virtualenv --python=$PYTHON pyenv
source pyenv/bin/activate
pip install --upgrade pip setuptools

# Create build directory
if [ -d "${BUILD}" ]; then
    rm -rf ${BUILD}
fi

mkdir -p ${BUILD}
cd ${BUILD}

# Configure
${CMAKE_COMMAND} \
      ${BUILD_HTTP_CACHE_CONFIGURATION} \
      -C ${LAMMPS_DIR}/cmake/presets/minimal.cmake \
      -C ${LAMMPS_DIR}/cmake/presets/kokkos-cuda.cmake \
      -D CMAKE_BUILD_TYPE="RelWithDebug" \
      -D CMAKE_CXX_COMPILER_LAUNCHER=ccache \
      -D CMAKE_CUDA_COMPILER_LAUNCHER=ccache \
      -D CMAKE_CXX_COMPILER=${LAMMPS_DIR}/lib/kokkos/bin/nvcc_wrapper \
      -D CMAKE_TUNE_FLAGS="-Wall -Wextra -Wno-unused-result" \
      -D CMAKE_INSTALL_PREFIX=${VIRTUAL_ENV} \
      -D BUILD_MPI=on \
      -D BUILD_OMP=on \
      -D BUILD_SHARED_LIBS=off \
      -D LAMMPS_SIZES=BIGBIG \
      -D LAMMPS_EXCEPTIONS=off \
      ${LAMMPS_DIR}/cmake || exit 1

# Build
${CMAKE_COMMAND} --build . -- -j ${LAMMPS_COMPILE_NPROC} || exit 1

# Install
# running install target repeats the compilation with Kokkos enabled
# ${CMAKE_COMMAND} --build . --target  install || exit 1
deactivate

ccache -s
