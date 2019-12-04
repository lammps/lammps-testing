#!/bin/bash
SCRIPTDIR="$(dirname "$(realpath "$0")")"

export LAMMPS_COMPILER=mpicxx
export CC=gcc
export CXX=g++

export LAMMPS_MODE=exe
export LAMMPS_MACH=mpi
export LAMMPS_TARGET=mpi
export LAMMPS_SIZE=BIGBIG

if [ "$JOBNAME" = "jenkins/openmpi/el7" ]
then
    export LAMMPS_CXX_STANDARD=CXX98
fi

LAMMPS_PACKAGES="yes-all \
                 no-lib \
                 no-mpiio \
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
                 yes-user-meamc \
                 yes-mpiio \
                 yes-user-lb"

. $SCRIPTDIR/LegacyBuild.sh
