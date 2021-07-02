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

if [ -z "${HTTP_CACHE_URL}" ] || [ -z "${LAMMPS_HTTP_CACHE_CONFIG}" ]
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

# 2021/04/27
# cannot test compiling with KOKKOS on Ubuntu18.04LTS anymore since
# Kokkos v3.4.0 now requires CMake 3.16. Can re-instate once we decide
# to move this test to a 20.04 container.
#      -C ${LAMMPS_DIR}/cmake/presets/kokkos-openmp.cmake \
#

# need to set this to avoid picking up parallel HDF5 on centos/fedora

export HDF5_ROOT=/usr

# Configure
${CMAKE_COMMAND} \
      ${BUILD_HTTP_CACHE_CONFIGURATION} \
      -C ${LAMMPS_DIR}/cmake/presets/clang.cmake \
      -C ${LAMMPS_DIR}/cmake/presets/most.cmake \
      -D CMAKE_BUILD_TYPE="RelWithDebug" \
      -D CMAKE_CXX_COMPILER_LAUNCHER=ccache \
      -D CMAKE_TUNE_FLAGS="-Wall -Wextra -Wno-unused-result" \
      -D CMAKE_INSTALL_PREFIX=${VIRTUAL_ENV} \
      -D BUILD_MPI=on \
      -D BUILD_OMP=on \
      -D BUILD_SHARED_LIBS=on \
      -D LAMMPS_SIZES=SMALLBIG \
      -D LAMMPS_EXCEPTIONS=on \
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
      -D PKG_ML-HDNN=on \
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
${CMAKE_COMMAND} --build . -- -j ${LAMMPS_COMPILE_NPROC} || exit 1

# Install
# running install target repeats the compilation with Kokkos enabled
${CMAKE_COMMAND} --build . --target  install || exit 1

MANIFEST=$PWD/install_manifest.txt

cd ${VIRTUAL_ENV}
sed s#${VIRTUAL_ENV}/## ${MANIFEST} > rel_install_manifest.txt

tar czvf lammps.tgz -T rel_install_manifest.txt

deactivate

ccache -s
