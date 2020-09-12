#!/bin/bash -x
SCRIPTDIR="$(dirname "$(realpath "$0")")"

export LAMMPS_MODE=static
export LAMMPS_MACH=serial
export LAMMPS_TARGET=serial
export LAMMPS_SIZES=SMALLSMALL
export LAMMPS_FLAGS="-O2 -g -fopenmp"
export LAMMPS_EXCEPT="-DLAMMPS_EXCEPTIONS"

LAMMPS_PACKAGES=(
                 yes-all
                 no-lib
                 no-mpiio
                 no-user-lb
                 no-user-smd
                 yes-user-molfile
                 yes-compress
                 yes-python
                 yes-poems
                 yes-user-colvars
                 yes-user-atc
                 yes-user-awpmd
                 yes-user-h5md
                 yes-user-dpd
                 yes-user-reaxc
                 yes-user-meamc
                )

. $SCRIPTDIR/legacy_build.sh
