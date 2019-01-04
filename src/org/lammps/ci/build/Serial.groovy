package org.lammps.ci.build

class Serial implements Serializable {
    def name = 'jenkins/serial'
    def steps

    Serial(steps) {
        this.steps = steps
    }

    private def enable_packages() {
        steps.stage('Enable packages') {
            steps.sh '''
            make -C lammps/src purge
            make -C lammps/src clean-all
            make -C lammps/src yes-all
            make -C lammps/src no-lib
            make -C lammps/src no-mpiio
            make -C lammps/src no-user-omp
            make -C lammps/src no-user-intel
            make -C lammps/src no-user-lb
            make -C lammps/src no-user-smd
            make -C lammps/src yes-user-molfile yes-compress yes-python
            make -C lammps/src yes-poems yes-user-colvars yes-user-awpmd yes-user-meamc
            make -C lammps/src yes-user-h5md
            '''
        }
    }

    private def build_libraries() {
        steps.stage('Building libraries') {
            steps.sh '''
            make -C lammps/lib/colvars -f Makefile.g++ clean
            make -C lammps/lib/poems -f Makefile.g++ CXX="${COMP}" clean
            make -C lammps/lib/awpmd -f Makefile.mpicc CC="${COMP}" clean
            make -C lammps/lib/h5md -f Makefile.h5cc clean
            make -C lammps/src/STUBS clean

            make -j 8 -C lammps/lib/colvars -f Makefile.g++ CXX="${COMP}"
            make -j 8 -C lammps/lib/poems -f Makefile.g++ CXX="${COMP}"
            make -j 8 -C lammps/lib/awpmd -f Makefile.mpicc CC="${COMP}"
            make -j 8 -C lammps/lib/h5md -f Makefile.h5cc
            '''
        }
    }

    def build() {
        steps.env.CCACHE_DIR = steps.pwd() + '/.ccache'
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

        enable_packages()
        build_libraries()

        steps.stage('Compiling') {
            steps.sh 'make -j 8 -C lammps/src ${MACH} MPICMD="${MPICMD}" CC="${COMP}" LINK="${COMP}" LMP_INC="${LMP_INC}" JPG_LIB="${JPG_LIB}" TAG="${TAG}-$CC" LMPFLAGS="${LMPFLAGS}"'
        }

        steps.sh 'ccache -s'
    }
}
