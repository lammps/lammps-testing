#!/bin/bash
SCRIPTDIR="$(dirname "$(realpath "$0")")"

export LAMMPS_MACH=mpi
export LAMMPS_TARGET=mpi
export LAMMPS_SIZE=SMALLBIG
export LAMMPS_COMPILER=mpicxx

export LAMMPS_PACKAGES=(
                        yes-asphere
                        yes-body
                        yes-class2
                        yes-colloid
                        yes-compress
                        yes-coreshell
                        yes-dipole
                        yes-granular
                        yes-kspace
                        yes-manybody
                        yes-mc
                        yes-misc
                        yes-molecule
                        yes-mpiio
                        yes-opt
                        yes-peri
                        yes-poems
                        yes-python
                        yes-qeq
                        yes-replica
                        yes-rigid
                        yes-shock
                        yes-snap
                        yes-spin
                        yes-srd
                        yes-voronoi
                        yes-user-atc
                        yes-user-awpmd
                        yes-user-bocs
                        yes-user-cgdna
                        yes-user-cgsdk
                        yes-user-colvars
                        yes-user-diffraction
                        yes-user-dpd
                        yes-user-drude
                        yes-user-eff
                        yes-user-fep
                        yes-user-lb
                        yes-user-manyfold
                        yes-user-meamc
                        yes-user-meso
                        yes-user-misc
                        yes-user-mofff
                        yes-user-molfile
                       )

. $SCRIPTDIR/LegacyBuild.sh
