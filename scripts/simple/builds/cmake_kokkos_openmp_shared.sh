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
      -C ${LAMMPS_DIR}/cmake/presets/clang.cmake \
      -C ${LAMMPS_DIR}/cmake/presets/most.cmake \
      -C ${LAMMPS_DIR}/cmake/presets/kokkos-openmp.cmake \
      -D CXX_COMPILER_LAUNCHER=ccache \
      -D CMAKE_CXX_FLAGS="${LAMMPS_CXX_COMPILER_FLAGS}" \
      -D CMAKE_C_FLAGS="${LAMMPS_C_COMPILER_FLAGS}" \
      -D CMAKE_INSTALL_PREFIX=${VIRTUAL_ENV} \
      -D CMAKE_TUNE_FLAGS="" \
      -D BUILD_MPI=on \
      -D BUILD_OMP=on \
      -D BUILD_SHARED_LIBS=on \
      -D LAMMPS_SIZES=SMALLBIG \
      -D LAMMPS_EXCEPTIONS=on \
      -D PKG_LATTE=on \
      -D PKG_MSCG=on \
      -D PKG_USER-ATC=on \
      -D PKG_USER-AWPMD=on \
      -D PKG_USER-BOCS=on \
      -D PKG_USER-EFF=on \
      -D PKG_USER-H5MD=on \
      -D PKG_USER-MANIFOLD=on \
      -D PKG_USER-MGPT=on \
      -D PKG_USER-MOLFILE=on \
      -D PKG_USER-NETCDF=on \
      -D PKG_USER-PHONON=on \
      -D PKG_USER-PLUMED=on \
      -D PKG_USER-PTM=on \
      -D PKG_USER-QTB=on \
      -D PKG_USER-SCAFACOS=on \
      -D PKG_USER-SDPD=on \
      -D PKG_USER-SMTBQ=on \
      -D PKG_USER-TALLY=on \
      -D PKG_MPIIO=on \
      -D PKG_USER-LB=on \
      ${LAMMPS_DIR}/cmake || exit 1

# Build
make -j ${LAMMPS_COMPILE_NPROC} || exit 1

# Install
make install || exit 1
deactivate

ccache -s
