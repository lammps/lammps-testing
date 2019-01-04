package org.lammps.ci.build

class Serial implements Serializable {
    def name = 'jenkins/serial'
    def steps

    Serial(steps) {
        this.steps = steps
    }

    def build() {
        steps.env.CCACHE_DIR= steps.pwd() + '/.ccache'
        steps.env.COMP     = 'g++'
        steps.env.MACH     = 'serial'
        steps.env.LMPFLAGS = '-sf off'
        steps.env.LMP_INC  = '-I../../src/STUBS -I/usr/include/hdf5/serial -DLAMMPS_SMALLSMALL -DFFT_KISSFFT -DLAMMPS_GZIP -DLAMMPS_PNG -DLAMMPS_JPEG -Wall -Wextra -Wno-unused-result -Wno-unused-parameter -Wno-maybe-uninitialized'
        steps.env.JPG_LIB  = '-L../../src/STUBS/ -L/usr/lib/x86_64-linux-gnu/hdf5/serial/ -lmpi_stubs -ljpeg -lpng -lz'

        steps.env.CC = 'gcc'
        steps.env.CXX = 'g++'
        steps.env.OMPI_CC = 'gcc'
        steps.env.OMPI_CXX = 'g++'

        steps.sh 'ccache -C'
        steps.sh 'ccache -M 5G'

        // clean up project directory
        steps.stage('Enabling modules') {
            steps.sh '''
            make -C src purge
            make -C src clean-all
            make -C src yes-all
            make -C src no-lib
            make -C src no-mpiio
            make -C src no-user-omp
            make -C src no-user-intel
            make -C src no-user-lb
            make -C src no-user-smd
            make -C src yes-user-molfile yes-compress yes-python
            make -C src yes-poems yes-user-colvars yes-user-awpmd yes-user-meamc
            make -C src yes-user-h5md
            '''
        }

        steps.stage('Building libraries') {
            steps.sh '''
            make -C lib/colvars -f Makefile.g++ clean
            make -C lib/poems -f Makefile.g++ CXX="${COMP}" clean
            make -C lib/awpmd -f Makefile.mpicc CC="${COMP}" clean
            make -C lib/h5md -f Makefile.h5cc clean
            make -C src/STUBS clean

            make -j 8 -C lib/colvars -f Makefile.g++ CXX="${COMP}"
            make -j 8 -C lib/poems -f Makefile.g++ CXX="${COMP}"
            make -j 8 -C lib/awpmd -f Makefile.mpicc CC="${COMP}"
            make -j 8 -C lib/h5md -f Makefile.h5cc
            '''
        }

        steps.stage('Compiling') {
            steps.sh 'make -j 8 -C src ${MACH} MPICMD="${MPICMD}" CC="${COMP}" LINK="${COMP}" LMP_INC="${LMP_INC}" JPG_LIB="${JPG_LIB}" TAG="${TAG}-$CC" LMPFLAGS="${LMPFLAGS}"'
        }

        steps.sh 'ccache -s'
    }
}
