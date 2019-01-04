#!/bin/bash
if [ ! -d lammps-testing ]
then
  git clone https://github.com/lammps/lammps-testing.git
fi

cd lammps-testing
git pull
cd ..

export CCACHE_DIR=$PWD/.ccache
export COMP=g++
export MACH=serial
export LMPFLAGS="-sf off"
export LMP_INC="-I../../src/STUBS -I/usr/include/hdf5/serial -DLAMMPS_SMALLBIG -DFFT_KISSFFT -DLAMMPS_GZIP -DLAMMPS_PNG -DLAMMPS_JPEG -Wall -Wextra -Wno-unused-result -Wno-unused-parameter -Wno-maybe-uninitialized"
export JPG_LIB="-L../../src/STUBS/ -L/usr/lib/x86_64-linux-gnu/hdf5/serial/ -lmpi_stubs -ljpeg -lpng -lz"

export CC=gcc
export CXX=g++
export OMPI_CC=gcc
export OMPI_CXX=g++

export LAMMPS_DIR=$PWD
export LAMMPS_MPI_MODE=openmpi
export LAMMPS_BINARY=$PWD/src/lmp_$MACH
export LAMMPS_TEST_MODES=serial
export LAMMPS_POTENTIALS=$PWD/potentials
export LC_ALL=C

ccache -C
ccache -M 5G
virtualenv pyenv

source pyenv/bin/activate
pip install nose
pip install nose2


make -C src purge
make -C src clean-all
make -C src yes-all
make -C src no-lib
make -C src no-mpiio
make -C src no-user-omp
make -C src no-user-intel
make -C src no-user-lb
make -C src no-user-smd


make -C lib/colvars -f Makefile.g++ clean
make -C lib/poems -f Makefile.g++ CXX="${COMP}" clean
make -C lib/awpmd -f Makefile.mpicc CC="${COMP}" clean
make -C lib/meam -f Makefile.gfortran CC=gcc F90=gfortran clean
make -C lib/h5md -f Makefile.h5cc clean

make -j 8 -C lib/colvars -f Makefile.g++ CXX="${COMP}"
make -j 8 -C lib/poems -f Makefile.g++ CXX="${COMP}"
make -j 8 -C lib/awpmd -f Makefile.mpicc CC="${COMP}"
make -j 8 -C lib/meam -f Makefile.gfortran CC=gcc F90=gfortran
make -j 8 -C lib/h5md -f Makefile.h5cc
make -C src/STUBS clean

cd lib/voronoi
rm -rf build
mkdir build
sed -i -e "s/http:\/\/math\.lbl\.gov\/voro++\/download\/dir/http:\/\/download\.lammps\.org\/thirdparty/g" Install.py
python2 Install.py -g
sed -i 's/CFLAGS=/CFLAGS=-fPIC /' voro++-0.4.6/config.mk
python2 Install.py -b -v voro++-0.4.6
cd ../..

make -C src yes-user-molfile yes-compress yes-python
make -C src yes-poems yes-voronoi yes-user-colvars yes-user-awpmd yes-meam
make -C src yes-user-h5md

make -j 8 -C src mode=shexe ${MACH} MPICMD="${MPICMD}" CC="${COMP}" LINK="${COMP}" LMP_INC="${LMP_INC}" JPG_LIB="${JPG_LIB}" TAG="${TAG}-$CC" LMPFLAGS="${LMPFLAGS}"

cd python
python install.py
cd ..
cd lammps-testing
env
python run_tests.py --processes 8 tests/test_commands.py tests/test_examples.py
cd ..
deactivate

ccache -s
