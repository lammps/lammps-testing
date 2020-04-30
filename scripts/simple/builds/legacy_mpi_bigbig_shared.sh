#!/bin/bash -x
SCRIPTDIR="$(dirname "$(realpath "$0")")"

export LAMMPS_COMPILER=mpicxx

export LAMMPS_MODE=shared
export LAMMPS_MACH=mpi
export LAMMPS_TARGET=mpi
export LAMMPS_SIZES=BIGBIG

LAMMPS_PACKAGES=(
                 yes-all
                 no-lib
                 no-mpiio
                 no-user-smd
                 yes-user-molfile
                 yes-compress
                 yes-python
                 yes-poems
                 yes-user-colvars
                 yes-user-awpmd
                 yes-user-meamc
                 yes-user-h5md
                 yes-user-dpd
                 yes-user-reaxc
                 yes-user-meamc
                 yes-mpiio
                 yes-user-lb
                )

. $SCRIPTDIR/legacy_build.sh
