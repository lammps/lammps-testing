#!/bin/bash
SCRIPTDIR="$(dirname "$(realpath "$0")")"

export JOBNAME="jenkins/cmake/serial"
export CMAKE_OPTIONS="-C $LAMMPS_DIR/cmake/presets/all_on.cmake \
	             -D CXX_COMPILER_LAUNCHER=ccache
                     -D CMAKE_CXX_FLAGS=\"-Wall -Wextra -Wno-unused-result -Wno-maybe-uninitialized\" \
                     -D PKG_USER-LB=off \
                     -D PKG_LATTE=off \
                     -D PKG_KIM=off \
                     -D PKG_USER-ADIOS=off \
                     -D PKG_USER-QUIP=off \
                     -D PKG_USER-QMMM=off \
                     -D PKG_USER-H5MD=off \
                     -D PKG_USER-SCAFACOS=off \
                     -D PKG_USER-VTK=off \
                     -D PKG_GPU=off \
                     -D PKG_KOKKOS=off \
                     -D PKG_MPIIO=off \
                     -D DOWNLOAD_VORO=on \
                     -D DOWNLOAD_MSCG=on \
                     -D DOWNLOAD_PLUMED=on \
                     -D BUILD_MPI=off \
                     -D BUILD_OMP=off"

. $SCRIPTDIR/CMakeBuild.sh
