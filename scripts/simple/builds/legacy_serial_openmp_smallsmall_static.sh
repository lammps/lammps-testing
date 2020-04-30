#!/bin/bash -x
SCRIPTDIR="$(dirname "$(realpath "$0")")"

export LAMMPS_MODE=static
export LAMMPS_MACH=serial
export LAMMPS_TARGET=serial
export LAMMPS_SIZES=SMALLSMALL

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
                 yes-user-awpmd
                 yes-user-h5md
                 yes-user-dpd
                 yes-user-reaxc
                 yes-user-meamc
                )

. $SCRIPTDIR/legacy_build.sh
