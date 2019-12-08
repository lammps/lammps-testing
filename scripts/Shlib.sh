#!/bin/bash
SCRIPTDIR="$(dirname "$(realpath "$0")")"

export LAMMPS_MODE=shlib
export LAMMPS_MACH=serial
export LAMMPS_TARGET=serial
export LAMMPS_SIZES=SMALLBIG
export LAMMPS_EXCEPT="-DLAMMPS_EXCEPTIONS"

if [ "$JOBNAME" = "jenkins/shlib/el7" ]
then
    export LAMMPS_CXX_STANDARD=CXX98
fi

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
                 yes-user-meamc
                 yes-user-h5md
                 yes-user-dpd
                 yes-user-reaxc
                 yes-user-meamc
                )

. $SCRIPTDIR/LegacyBuild.sh
