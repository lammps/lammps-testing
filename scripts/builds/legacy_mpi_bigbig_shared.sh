#!/bin/bash -x
SCRIPTDIR="$(dirname "$(realpath "$0")")"

export LAMMPS_COMPILER=mpicxx

export LAMMPS_MODE=shared
export LAMMPS_MACH=mpi
export LAMMPS_TARGET=mpi
export LAMMPS_SIZES=BIGBIG
export LAMMPS_FLAGS="-O3 -g"

LAMMPS_PACKAGES=(
                 yes-all
                 no-lib
                 no-mpiio
                 no-machdyn
                 yes-molfile
                 yes-compress
                 yes-poems
                 yes-colvars
                 yes-awpmd
                 yes-h5md
                 yes-dpd-react
                 yes-reaxff
                 yes-meam
                 yes-mpiio
                 yes-latboltz
                )
# temporarily disabled. fails to link ML-IAP /w Python on some Fedora versions
#                 yes-python

. $SCRIPTDIR/legacy_build.sh
