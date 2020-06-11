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

# Configure
${CMAKE_COMMAND} -C ${LAMMPS_DIR}/cmake/presets/all_off.cmake \
      -D CMAKE_BUILD_TYPE="RelWithDebug" \
      -D CMAKE_CXX_COMPILER_LAUNCHER=ccache \
      -D CMAKE_TUNE_FLAGS="-O3 -Wall -Wextra -Wno-unused-result -Wno-unused-parameter -Wno-maybe-uninitialized" \
      -D CMAKE_INSTALL_PREFIX=${VIRTUAL_ENV} \
      -D ENABLE_COVERAGE=off \
      -D BUILD_MPI=on \
      -D BUILD_OMP=off \
      -D BUILD_SHARED_LIBS=on \
      -D LAMMPS_SIZES=SMALLBIG \
      -D LAMMPS_EXCEPTIONS=on \
      -D PKG_ASPHERE=on \
      -D PKG_BODY=on \
      -D PKG_CLASS2=on \
      -D PKG_COLLOID=on \
      -D PKG_COMPRESS=on \
      -D PKG_CORESHELL=on \
      -D PKG_DIPOLE=on \
      -D PKG_GRANULAR=on \
      -D PKG_KSPACE=on \
      -D PKG_MANYBODY=on \
      -D PKG_MC=on \
      -D PKG_MISC=on \
      -D PKG_MOLECULE=on \
      -D PKG_OPT=on \
      -D PKG_PERI=on \
      -D PKG_POEMS=on \
      -D PKG_PYTHON=on \
      -D PKG_QEQ=on \
      -D PKG_REPLICA=on \
      -D PKG_RIGID=on \
      -D PKG_SHOCK=on \
      -D PKG_SNAP=on \
      -D PKG_SPIN=on \
      -D PKG_SRD=on \
      -D PKG_USER-AWPMD=on \
      -D PKG_USER-BOCS=on \
      -D PKG_USER-CGDNA=on \
      -D PKG_USER-CGSDK=on \
      -D PKG_USER-COLVARS=on \
      -D PKG_USER-DIFFRACTION=on \
      -D PKG_USER-DPD=on \
      -D PKG_USER-DRUDE=on \
      -D PKG_USER-EFF=on \
      -D PKG_USER-FEP=on \
      -D PKG_USER-H5MD=on \
      -D PKG_USER-MANIFOLD=on \
      -D PKG_USER-MEAMC=on \
      -D PKG_USER-MESODPD=on \
      -D PKG_USER-MGPT=on \
      -D PKG_USER-MISC=on \
      -D PKG_USER-MOFFF=on \
      -D PKG_USER-MOLFILE=on \
      -D PKG_USER-PHONON=on \
      -D PKG_USER-PTM=on \
      -D PKG_USER-QTB=on \
      -D PKG_USER-REAXC=on \
      -D PKG_USER-SDPD=on \
      -D PKG_USER-SMTBQ=on \
      -D PKG_USER-SPH=on \
      -D PKG_USER-TALLY=on \
      -D PKG_USER-UEF=on \
      -D PKG_USER-YAFF=on \
      -D PKG_MPIIO=on \
      -D PKG_USER-LB=on \
      -D PKG_VORONOI=on \
      -D PKG_USER-ATC=on \
      ${LAMMPS_DIR}/cmake || exit 1

# Build
make -j ${LAMMPS_COMPILE_NPROC} || exit 1

# Install
make install || exit 1
deactivate

ccache -s
