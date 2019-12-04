#!/bin/bash
SCRIPTDIR="$(dirname "$(realpath "$0")")"

export LAMMPS_COMPILER=clang++
export CC=clang
export CXX=clang++

. $SCRIPTDIR/Shlib.sh
