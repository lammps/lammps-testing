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
${CMAKE_COMMAND} \
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
cmake --build . -- -j ${LAMMPS_COMPILE_NPROC} || exit 1

# Install
# running install target repeats the compilation with Kokkos enabled
# cmake --build . --target  install || exit 1
deactivate

ccache -s
