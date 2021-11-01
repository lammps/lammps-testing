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

export PYTHON=$(which python3)

# Set up environment
virtualenv --python=$PYTHON pyenv
source pyenv/bin/activate
pip install --upgrade pip setuptools

# Create build directory
if [ -d "${BUILD}" ]; then
    rm -rf ${BUILD}
fi

mkdir -p ${BUILD}
cd ${BUILD}

# need to set this to avoid picking up parallel HDF5 on centos/fedora
export HDF5_ROOT=/usr

# add coverity tools to PATH
export PATH=/opt/coverity/bin:$PATH

# Configure
${CMAKE_COMMAND} \
      -C ${LAMMPS_DIR}/cmake/presets/clang.cmake \
      -C ${LAMMPS_DIR}/cmake/presets/most.cmake \
      -C ${LAMMPS_DIR}/cmake/presets/kokkos-openmp.cmake \
      -D CMAKE_BUILD_TYPE="RelWithDebug" \
      -D CMAKE_TUNE_FLAGS="-Wall -Wextra -Wno-unused-result" \
      -D CMAKE_INSTALL_PREFIX=${VIRTUAL_ENV} \
      -D BUILD_MPI=on \
      -D BUILD_OMP=on \
      -D BUILD_SHARED_LIBS=on \
      -D LAMMPS_SIZES=SMALLBIG \
      -D LAMMPS_EXCEPTIONS=off \
      -D PKG_MESSAGE=on \
      -D PKG_MPIIO=on \
      -D PKG_ATC=on \
      -D PKG_AWPMD=on \
      -D PKG_BOCS=on \
      -D PKG_EFF=on \
      -D PKG_H5MD=on \
      -D PKG_INTEL=on \
      -D PKG_LATBOLTZ=on \
      -D PKG_MANIFOLD=on \
      -D PKG_MGPT=on \
      -D PKG_ML-HDNNP=on \
      -D PKG_ML-PACE=on \
      -D PKG_ML-RANN=on \
      -D PKG_MOLFILE=on \
      -D PKG_NETCDF=on \
      -D PKG_PTM=on \
      -D PKG_QTB=on \
      -D PKG_SMTBQ=on \
      -D PKG_TALLY=on \
      ${LAMMPS_DIR}/cmake || exit 1

# Build
cov-build --dir cov-int cmake --build . -- -j ${LAMMPS_COMPILE_NPROC} || exit 1

# Create tarball with scan results
tar czvf lammps.tgz cov-int
