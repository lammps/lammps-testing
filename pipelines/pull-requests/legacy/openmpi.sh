export PATH=/usr/lib/ccache:$PATH
export CCACHE_DIR=$PWD/.ccache

export LMPFLAGS='-sf off'
export COMP='mpicxx'
export MACH='mpi'
export MPICMD='mpirun -np 4'
export LMP_INC='-I/usr/include/hdf5/serial -DFFT_KISSFFT -DLAMMPS_GZIP -DLAMMPS_PNG -DLAMMPS_JPEG -DLAMMPS_BIGBIG -Wall -Wextra -Wno-unused-result -Wno-unused-parameter -Wno-maybe-uninitialized'
export JPG_LIB='-L/usr/lib/x86_64-linux-gnu/hdf5/serial/ -ljpeg -lpng -lz'

export CC=gcc
export CXX=g++
export OMPI_CC=gcc
export OMPI_CXX=g++


ccache -C
ccache -M 5G

make -C src purge
make -C src clean-all
make -C src yes-all
make -C src no-lib
make -C src no-user-omp
make -C src no-user-intel
make -C src no-user-smd

make -C lib/colvars -f Makefile.g++ clean
make -C lib/poems -f Makefile.g++ CXX="${COMP}" clean
#make -C lib/voronoi -f Makefile.g++ CXX="${COMP}" clean
make -C lib/awpmd -f Makefile.mpicc CC="${COMP}" clean
make -C lib/h5md -f Makefile.h5cc clean

make -j 8 -C lib/colvars -f Makefile.g++ CXX="${COMP}"
make -j 8 -C lib/poems -f Makefile.g++ CXX="${COMP}"
#make -j 8 -C lib/voronoi -f Makefile.g++ CXX="${COMP}"
make -j 8 -C lib/awpmd -f Makefile.mpicc CC="${COMP}"
make -j 8 -C lib/h5md -f Makefile.h5cc

if [ -d lib/meam ]; then
  make -C lib/meam -f Makefile.gfortran CC=gcc F90=gfortran clean
  make -j 8 -C lib/meam -f Makefile.gfortran CC=gcc F90=gfortran
  make -C src yes-meam
fi

#make -C src yes-user-smd yes-user-molfile yes-compress yes-python
make -C src yes-user-molfile yes-compress yes-python

#make -C src yes-poems yes-voronoi yes-user-colvars yes-user-awpmd yes-meam
make -C src yes-poems yes-user-colvars yes-user-awpmd

make -C src yes-user-h5md
make -C src yes-mpiio yes-user-lb

make -C src yes-user-dpd

make -j 8 -C src ${MACH} MPICMD="${MPICMD}" CC="${COMP}" LINK="${COMP}" LMP_INC="${LMP_INC}" JPG_LIB="${JPG_LIB}" TAG="${TAG}-$CC" LMPFLAGS="${LMPFLAGS}"
