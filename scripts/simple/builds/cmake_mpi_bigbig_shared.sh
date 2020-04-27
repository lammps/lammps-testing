#!/bin/bash -x
if [ -z "${LAMMPS_DIR}" ]
then
        echo "Must set LAMMPS_DIR environment variable"
        exit 1
fi
BUILD=build-$(basename $0 .sh)

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
LAMMPS_CXX_COMPILER_FLAGS="-Wall -Wextra -Wno-unused-result -Wno-maybe-uninitialized"
LAMMPS_C_COMPILER_FLAGS="-Wall -Wextra -Wno-unused-result -Wno-maybe-uninitialized"

export CCACHE_DIR="$PWD/.ccache"
export PYTHON=$(which python3)

# Set up environment
ccache -M 5G
virtualenv --python=$PYTHON pyenv
source pyenv/bin/activate

# Create build directory
if [ -d "${BUILD}" ]; then
    rm -rf ${BUILD}
fi

mkdir -p ${BUILD}
cd ${BUILD}

# Configure
${CMAKE_COMMAND} -G Ninja \
      -C ${LAMMPS_DIR}/cmake/presets/most.cmake \
      -D CMAKE_CXX_COMPILER_LAUNCHER=ccache \
      -D CMAKE_CXX_FLAGS="${LAMMPS_CXX_COMPILER_FLAGS}" \
      -D CMAKE_C_FLAGS="${LAMMPS_C_COMPILER_FLAGS}" \
      -D CMAKE_INSTALL_PREFIX=${VIRTUAL_ENV} \
      -D BUILD_MPI=on \
      -D BUILD_OMP=off \
      -D BUILD_SHARED_LIBS=on \
      -D LAMMPS_SIZES=BIGBIG \
      -D LAMMPS_EXCEPTIONS=on \
      -D PKG_USER-AWPMD=on \
      -D PKG_USER-BOCS=on \
      -D PKG_USER-EFF=on \
      -D PKG_USER-H5MD=on \
      -D PKG_USER-MANIFOLD=on \
      -D PKG_USER-MOLFILE=on \
      -D PKG_USER-PTM=on \
      -D PKG_USER-QTB=on \
      -D PKG_USER-SDPD=on \
      -D PKG_USER-SMTBQ=on \
      -D PKG_USER-TALLY=on \
      -D PKG_USER-OMP=on \
      -D PKG_USER-INTEL=on \
      -D PKG_MPIIO=on \
      -D PKG_USER-LB=on \
      ${LAMMPS_DIR}/cmake || exit 1

# Build
ninja -j ${LAMMPS_COMPILE_NPROC} || exit 1

# Install
ninja install || exit 1
deactivate

ccache -s
