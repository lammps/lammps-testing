#!/bin/bash -x
SCRIPT_DIR="$(dirname "$(realpath "$0")")"
SCRIPT_BASE_DIR=$LAMMPS_TESTING_DIR/scripts

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
    BUILD=build-omp
fi
export BUILD

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

if [ -z "${HTTP_CACHE_URL}" ] || [ -z "${LAMMPS_HTTP_CACHE_CONFIG}" ]
then
    BUILD_HTTP_CACHE_CONFIGURATION=""
else
    BUILD_HTTP_CACHE_CONFIGURATION="-D LAMMPS_DOWNLOADS_URL=${HTTP_CACHE_URL} -C ${LAMMPS_HTTP_CACHE_CONFIG}"
fi

export PYTHON=$(which python3)

# Set up environment
ccache -M 10G

$SCRIPT_BASE_DIR/common/init_venv.sh
$SCRIPT_BASE_DIR/common/init_testing_venv.sh

source pyenv/bin/activate

# Create build directory
if [ -d "${BUILD}" ]; then
    rm -rf ${BUILD}
fi

mkdir -p ${BUILD}
cd ${BUILD}

# Configure
${CMAKE_COMMAND} \
      ${BUILD_HTTP_CACHE_CONFIGURATION} \
      -C ${LAMMPS_DIR}/cmake/presets/most.cmake \
      -D CMAKE_BUILD_TYPE="RelWithDebug" \
      -D CMAKE_CXX_COMPILER_LAUNCHER=ccache \
      -D CMAKE_TUNE_FLAGS="-O3 -Wall -Wextra -Wno-unused-result -Wno-unused-parameter -Wno-maybe-uninitialized" \
      -D CMAKE_INSTALL_PREFIX=${VIRTUAL_ENV} \
      -D ENABLE_COVERAGE=off \
      -D BUILD_MPI=on \
      -D BUILD_OMP=on \
      -D BUILD_SHARED_LIBS=on \
      -D LAMMPS_SIZES=SMALLBIG \
      -D LAMMPS_EXCEPTIONS=on \
      -D PKG_ATC=on \
      -D PKG_AWPMD=on \
      -D PKG_H5MD=on \
      -D PKG_LATBOLTZ=on \
      -D PKG_MANIFOLD=on \
      -D PKG_MGPT=on \
      -D PKG_MOLFILE=on \
      -D PKG_MPIIO=on \
      -D PKG_PTM=on \
      -D PKG_PYTHON=on \
      -D PKG_QTB=on \
      -D PKG_SMTBQ=on \
      -D PKG_TALLY=on \
      ${LAMMPS_DIR}/cmake || exit 1

# Build
make -j ${LAMMPS_COMPILE_NPROC} || exit 1

# Install
make install || exit 1
make install-python || exit 1
deactivate

ccache -s
