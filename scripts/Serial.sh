#!/bin/bash
SCRIPTDIR="$(dirname "$(realpath "$0")")"

export LAMMPS_MODE=exe
export LAMMPS_MACH=serial
export LAMMPS_TARGET=serial
export LAMMPS_SIZE=SMALLSMALL

if [ "$JOBNAME" = "jenkins/serial/el7" ]
then
    export LAMMPS_CXX_STANDARD=CXX98
fi

LAMMPS_PACKAGES="yes-all \
                 no-lib \
                 no-mpiio \
                 no-user-omp \
                 no-user-intel \
                 no-user-lb \
                 no-user-smd \
                 yes-user-molfile \
                 yes-compress \
                 yes-python \
                 yes-poems \
                 yes-user-colvars \
                 yes-user-awpmd \
                 yes-user-meamc \
                 yes-user-h5md \
                 yes-user-dpd \
                 yes-user-reaxc \
                 yes-user-meamc"

. $SCRIPTDIR/LegacyBuild.sh
