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

# init OneAPI
source /opt/intel/oneapi/setvars.sh

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
$PYTHON -m venv pyenv
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
# Configure
${CMAKE_COMMAND} -G Ninja \
      ${BUILD_HTTP_CACHE_CONFIGURATION} \
      -D DOWNLOAD_POTENTIALS=off \
      -C ${LAMMPS_DIR}/cmake/presets/kokkos-sycl-intel.cmake \
      -C ${LAMMPS_DIR}/cmake/presets/most.cmake \
      -D CMAKE_BUILD_TYPE="RelWithDebug" \
      -D CMAKE_TUNE_FLAGS="-Wall -Wextra" \
      -D CMAKE_INSTALL_PREFIX=${VIRTUAL_ENV} \
      -D BUILD_MPI=off \
      -D BUILD_OMP=on \
      -D BUILD_SHARED_LIBS=off \
      -D LAMMPS_SIZES=BIGBIG \
      -D LAMMPS_EXCEPTIONS=on \
      -D FFT=MKL \
      -D PKG_MPIIO=on \
      -D PKG_AWPMD=on \
      -D PKG_BOCS=on \
      -D PKG_EFF=on \
      -D PKG_H5MD=on \
      -D PKG_INTEL=on \
      -D PKG_LATBOLTZ=on \
      -D PKG_MANIFOLD=on \
      -D PKG_MOLFILE=on \
      -D PKG_NETCDF=on \
      -D PKG_PTM=on \
      -D PKG_PYTHON=on \
      -D PKG_QTB=on \
      -D PKG_SMTBQ=on \
      -D PKG_TALLY=on \
      ${LAMMPS_DIR}/cmake || exit 1

# Build
${CMAKE_COMMAND} --build . -- -j ${LAMMPS_COMPILE_NPROC} || exit 1

# Install
${CMAKE_COMMAND} --build . --target  install || exit 1
deactivate

ccache -s
