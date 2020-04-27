#!/bin/bash -x
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
LAMMPS_CXX_COMPILER_FLAGS="-Wall -Wextra -Wno-unused-result"
LAMMPS_C_COMPILER_FLAGS="-Wall -Wextra -Wno-unused-result"

export CCACHE_DIR="$PWD/.ccache"
export PYTHON=$(which python3)

# Set up environment
ccache -M 5G
virtualenv --python=$PYTHON pyenv
source pyenv/bin/activate

# Configure
${CMAKE_COMMAND} \
      -C ${LAMMPS_DIR}/cmake/presets/minimal.cmake \
      -C ${LAMMPS_DIR}/cmake/presets/kokkos-cuda.cmake \
      -D CXX_COMPILER_LAUNCHER=ccache \
      -D CMAKE_CXX_COMPILER=${LAMMPS_DIR}/lib/kokkos/bin/nvcc_wrapper \
      -D CMAKE_CXX_FLAGS="${LAMMPS_CXX_COMPILER_FLAGS}" \
      -D CMAKE_C_FLAGS="${LAMMPS_C_COMPILER_FLAGS}" \
      -D CMAKE_INSTALL_PREFIX=${VIRTUAL_ENV} \
      -D CMAKE_TUNE_FLAGS="" \
      -D BUILD_MPI=on \
      -D BUILD_OMP=on \
      -D PKG_GPU=on \
      -D GPU_API=cuda \
      -D GPU_ARCH=sm_50 \
      -D GPU_PREC=double \
      -D BUILD_SHARED_LIBS=off \
      -D LAMMPS_SIZES=BIGBIG \
      -D LAMMPS_EXCEPTIONS=off \
      ${LAMMPS_DIR}/cmake || exit 1

# Build
make -j ${LAMMPS_COMPILE_NPROC} || exit 1

# Install
make install || exit 1
deactivate

ccache -s
