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

export PYTHON=$(which python3)

# Set up environment
ccache -M 10G

$SCRIPT_BASE_DIR/common/init_testing_venv.sh

source pyenv/bin/activate

# Create build directory
if [ -d "${BUILD}" ]; then
    rm -rf ${BUILD}
fi

mkdir -p ${BUILD}
cd ${BUILD}

source kim-api-activate

# Configure
${CMAKE_COMMAND} \
      -C ${LAMMPS_DIR}/cmake/presets/minimal.cmake \
      -D CMAKE_BUILD_TYPE="RelWithDebug" \
      -D CMAKE_CXX_COMPILER_LAUNCHER=ccache \
      -D CMAKE_TUNE_FLAGS="-O0 -Wall -Wextra -Wno-unused-result" \
      -D CMAKE_INSTALL_PREFIX=${VIRTUAL_ENV} \
      -D BUILD_MPI=on \
      -D BUILD_OMP=on \
      -D PKG_ASPHERE=on \
      -D PKG_BODY=on \
      -D PKG_CLASS2=on \
      -D PKG_COLLOID=on \
      -D PKG_CORESHELL=on \
      -D PKG_DIPOLE=on \
      -D PKG_GRANULAR=on \
      -D PKG_KIM=on \
      -D PKG_KSPACE=on \
      -D PKG_MANYBODY=on \
      -D PKG_MC=on \
      -D PKG_MISC=on \
      -D PKG_MLIAP=on \
      -D PKG_MOLECULE=on \
      -D PKG_MPIIO=on \
      -D PKG_OPT=on \
      -D PKG_PERI=on \
      -D PKG_POEMS=on \
      -D PKG_PYTHON=on \
      -D PKG_REPLICA=on \
      -D PKG_RIGID=ON \
      -D PKG_SHOCK=on \
      -D PKG_SNAP=on \
      -D PKG_USER-CGDNA=on \
      -D PKG_USER-INTEL=on \
      -D PKG_USER-MISC=on \
      -D PKG_USER-OMP=on \
      -D PKG_USER-QTB=on \
      -D PKG_USER-REAXC=on \
      -D BUILD_SHARED_LIBS=on \
      -D LAMMPS_SIZES=BIGBIG \
      -D LAMMPS_EXCEPTIONS=on \
      -D ENABLE_TESTING=on \
      -D ENABLE_COVERAGE=on \
      ${LAMMPS_DIR}/cmake || exit 1

# Build
cmake --build . -- -j ${LAMMPS_COMPILE_NPROC} || exit 1

ccache -s
