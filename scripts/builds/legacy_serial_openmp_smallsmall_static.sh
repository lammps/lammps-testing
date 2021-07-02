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
                 no-latboltz
                 no-machdyn
                 yes-molfile
                 yes-compress
                 yes-python
                 yes-poems
                 yes-colvars
                 yes-atc
                 yes-awpmd
                 yes-h5md
                 yes-dpd-reaxct
                 yes-reaxff
                 yes-meam
                )

. $SCRIPTDIR/legacy_build.sh
