#!/bin/bash
SCRIPTDIR="$(dirname "$(realpath "$0")")"

export CC=clang
export CXX=clang++
export LAMMPS_EXCEPT="-DLAMMPS_EXCEPTIONS"

. $SCRIPTDIR/OpenMPI.sh
