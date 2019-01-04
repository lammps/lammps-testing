#!/bin/bash

if [ ! -d lammps-testing ]
then
  git clone https://github.com/lammps/lammps-testing.git
fi

cd lammps-testing
git pull
cd ..

export CCACHE_DIR=$PWD/.ccache
export COMP=mpicxx
export MACH=mpi
export LMP_INC='-DLAMMPS_SMALLBIG -DLAMMPS_GZIP -DLAMMPS_PNG -DLAMMPS_JPEG -Wall -Wextra -Wno-unused-result -Wno-unused-parameter -Wno-maybe-uninitialized'
export JPG_LIB='-ljpeg -lpng -lz'

export CC=gcc
export CXX=g++
export OMPI_CC=gcc
export OMPI_CXX=g++

export LAMMPS_DIR=$PWD
export LAMMPS_MPI_MODE=openmpi
export LAMMPS_BINARY=$PWD/src/lmp_$MACH
export LAMMPS_TEST_MODES=serial
export LAMMPS_POTENTIALS=$PWD/potentials

ccache -C
ccache -M 5G

virtualenv --python=$(which python2) pyenv2

source pyenv2/bin/activate
pip install nose
pip install nose2
deactivate

make -C src clean-all
make -C lib/atc -f Makefile.mpic++ EXTRAMAKE="Makefile.lammps.installed" clean
make -C lib/colvars -f Makefile.g++ clean
make -C lib/poems -f Makefile.g++ CXX="${COMP}" clean
make -C lib/awpmd -f Makefile.mpicc CC="${COMP}" clean
#make -C lib/meam -f Makefile.gfortran CC=gcc F90=gfortran clean
make -C lib/qmmm -f Makefile.gfortran clean
#make -C lib/reax -f Makefile.gfortran clean

make -j 8 -C lib/atc -f Makefile.mpic++ EXTRAMAKE="Makefile.lammps.installed"
make -j 8 -C lib/colvars -f Makefile.g++ CXX="${COMP}"
make -j 8 -C lib/poems -f Makefile.g++ CXX="${COMP}"
make -j 8 -C lib/awpmd -f Makefile.mpicc CC="${COMP}"
#make -j 8 -C lib/meam -f Makefile.gfortran CC=gcc F90=gfortran
make -j 8 -C lib/qmmm -f Makefile.gfortran
#make -j 8 -C lib/reax -f Makefile.gfortran

cd lib/voronoi
python2 Install.py -b
cd ../..

make -C src yes-asphere
make -C src yes-body
make -C src yes-class2
make -C src yes-colloid
make -C src yes-compress
make -C src yes-coreshell
make -C src yes-dipole
make -C src yes-fld
make -C src yes-granular
make -C src yes-kspace
make -C src yes-manybody
make -C src yes-mc
#make -C src yes-meam
make -C src yes-misc
make -C src yes-molecule
make -C src yes-mpiio
make -C src yes-opt
make -C src yes-peri
make -C src yes-poems
make -C src yes-python
make -C src yes-qeq
#make -C src yes-reax
make -C src yes-replica
make -C src yes-rigid
make -C src yes-shock
make -C src yes-snap
make -C src yes-srd
make -C src yes-voronoi
make -C src yes-xtc
make -C src yes-user-atc
make -C src yes-user-awpmd
make -C src yes-user-cg-cmm
make -C src yes-user-colvars
make -C src yes-user-diffraction
make -C src yes-user-dpd
make -C src yes-user-drude
make -C src yes-user-eff
make -C src yes-user-fep
make -C src yes-user-lb
make -C src yes-user-misc
make -C src yes-user-molfile
make -C src yes-user-phonon
make -C src yes-user-qmmm
make -C src yes-user-qtb
make -C src yes-user-meamc
make -C src yes-user-reaxc
make -C src yes-user-sph
make -C src yes-user-tally
make -C src yes-user-smtbq

make -j 8 -C src mode=shexe ${MACH} CC="${COMP}" LINK="${COMP}" LMP_INC="${LMP_INC}" JPG_LIB="${JPG_LIB}"

rm -rf lammps-testing/tests/examples/USER/eff
rm -rf lammps-testing/tests/examples/USER/misc/imd
rm -rf lammps-testing/tests/examples/USER/fep
rm -rf lammps-testing/tests/examples/USER/lb
rm -rf lammps-testing/tests/examples/HEAT
rm -rf lammps-testing/tests/examples/COUPLE
rm -rf lammps-testing/tests/examples/gcmc

source pyenv2/bin/activate
cd python
python install.py
cd ..
rm *.out *.xml || true

python2 lammps-testing/lammps_testing/regression.py 8 "mpiexec -np 8 ${LAMMPS_BINARY} -v CORES 8" lammps-testing/tests/examples -exclude kim mscg nemd prd tad neb VISCOSITY ASPHERE USER/mgpt USER/dpd/dpdrx-shardlow balance accelerate USER/atc USER/quip USER/misc/grem USER/misc/i-pi USER/misc/pimd USER/cg-cmm 2>&1 |tee test0.out
python2 lammps-testing/lammps_testing/regression.py 8 "mpiexec -np 8 ${LAMMPS_BINARY} -partition 4x2 -v CORES 8" lammps-testing/tests/examples -only prd 2>&1 |tee test1.out
deactivate

python lammps-testing/lammps_testing/generate_regression_xml.py --test-dir $PWD/lammps-testing/tests/ --log-file test0.out --out-file regression_00.xml
python lammps-testing/lammps_testing/generate_regression_xml.py --test-dir $PWD/lammps-testing/tests/ --log-file test1.out --out-file regression_01.xml

ccache -s
