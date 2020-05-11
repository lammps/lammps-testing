#!/bin/bash -x
SCRIPT_DIR="$(dirname "$(realpath "$0")")"
SCRIPT_BASE_DIR=$LAMMPS_TESTING_DIR/scripts/simple

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

export CCACHE_DIR="$PWD/.ccache"
export PYTHON=$(which python3)

# Set up environment
ccache -M 5G

$SCRIPT_BASE_DIR/common/init_testing_venv.sh

source pyenv/bin/activate

# Create build directory
if [ -d "${BUILD}" ]; then
    rm -rf ${BUILD}
fi

mkdir -p ${BUILD}
cd ${BUILD}

# need to set this to avoid picking up parallel HDF5 on centos/fedora
export HDF5_ROOT=/usr
# Configure
${CMAKE_COMMAND} \
      -C ${LAMMPS_DIR}/cmake/presets/most.cmake \
      -D CMAKE_BUILD_TYPE="RelWithDebug" \
      -D CMAKE_CXX_COMPILER_LAUNCHER=ccache \
      -D CMAKE_TUNE_FLAGS="-O3 -Wall -Wextra -Wno-unused-result" \
      -D CMAKE_INSTALL_PREFIX=${VIRTUAL_ENV} \
      -D BUILD_MPI=on \
      -D BUILD_OMP=off \
      -D BUILD_SHARED_LIBS=on \
      -D LAMMPS_SIZES=SMALLBIG \
      -D LAMMPS_EXCEPTIONS=on \
      -D PKG_MESSAGE=on \
      -D PKG_MPIIO=on \
      -D PKG_USER-ATC=on \
      -D PKG_USER-AWPMD=on \
      -D PKG_USER-BOCS=on \
      -D PKG_USER-EFF=on \
      -D PKG_USER-H5MD=on \
      -D PKG_USER-INTEL=on \
      -D PKG_USER-LB=on \
      -D PKG_USER-MANIFOLD=on \
      -D PKG_USER-MGPT=on \
      -D PKG_USER-MOLFILE=on \
      -D PKG_USER-NETCDF=on \
      -D PKG_USER-PTM=on \
      -D PKG_USER-QTB=on \
      -D PKG_USER-SDPD=on \
      -D PKG_USER-SMTBQ=on \
      -D PKG_USER-TALLY=on \
      ${LAMMPS_DIR}/cmake || exit 1

# Build
cmake --build . -- -j ${LAMMPS_COMPILE_NPROC} || exit 1

# Install
# running install target repeats the compilation with Kokkos enabled
cmake --build . --target  install || exit 1

ccache -s
