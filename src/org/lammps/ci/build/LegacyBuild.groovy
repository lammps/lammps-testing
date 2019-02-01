package org.lammps.ci.build

enum LAMMPS_MODE {
    exe,
    shexe,
    shlib
}

enum LAMMPS_SIZES {
    SMALLSMALL,
    SMALLBIG,
    BIGBIG
}

class LegacyBuild implements Serializable {
    protected def name
    protected def steps

    def compiler = 'g++'
    def c_compiler = 'gcc'
    def cxx_compiler = 'g++'
    def lammps_mode = LAMMPS_MODE.exe
    def lammps_mach = 'serial'
    def lammps_target = 'serial'
    def lammps_size = LAMMPS_SIZES.SMALLBIG
    def packages = []
    def message = ''

    LegacyBuild(name, steps) {
        this.name  = name
        this.steps = steps
    }

    protected def enable_packages() {
        steps.stage('Enable packages') {
            steps.sh '''#!/bin/bash -l
            make -C lammps/src purge
            make -C lammps/src clean-all
            '''

            packages.each {
                steps.sh "make -C lammps/src $it"
            }
        }
    }

    protected def build_libraries() {
        steps.stage('Building libraries') {
            steps.sh '''#!/bin/bash -l
            make -C lammps/src/STUBS clean
            '''

            if('yes-user-colvars' in packages) {
                steps.sh '''#!/bin/bash -l
                make -C lammps/lib/colvars -f Makefile.${MACH} clean
                make -j 8 -C lammps/lib/colvars -f Makefile.${MACH} CXX="${COMP}"
                '''
            }

            if('yes-poems' in packages) {
                steps.sh '''#!/bin/bash -l
                make -C lammps/lib/poems -f Makefile.${MACH} clean
                make -j 8 -C lammps/lib/poems -f Makefile.${MACH} CC="${COMP}" LINK="${COMP}"
                '''
            }

            if('yes-user-awpmd' in packages) {
                steps.sh '''#!/bin/bash -l
                make -C lammps/lib/awpmd -f Makefile.${MACH} clean
                make -j 8 -C lammps/lib/awpmd -f Makefile.${MACH} CC="${COMP}" EXTRAMAKE=Makefile.lammps.installed
                '''
            }

            if('yes-user-h5md' in packages) {
                steps.sh '''#!/bin/bash -l
                make -C lammps/lib/h5md -f Makefile.h5cc clean
                make -j 8 -C lammps/lib/h5md -f Makefile.h5cc
                '''
            }

            if('yes-voronoi' in packages) {
                steps.sh '''#!/bin/bash -l
                make -C lammps/src lib-voronoi args="-b"
                '''
            }

            if('yes-user-atc' in packages) {
                steps.sh '''#!/bin/bash -l
                make -C lammps/lib/atc -f Makefile.${MACH} clean
                make -j 8 -C lammps/lib/atc -f Makefile.${MACH} EXTRAMAKE="Makefile.lammps.installed"
                '''
            }

            if('yes-user-qmmm' in packages) {
                steps.sh '''#!/bin/bash -l
                make -C lammps/lib/qmmm -f Makefile.${MACH} clean
                make -j 8 -C lammps/lib/qmmm -f Makefile.${MACH}
                '''
            }
        }
    }

    def configure() {
        steps.env.CCACHE_DIR = steps.pwd() + '/.ccache'
        steps.env.COMP     = compiler
        steps.env.MACH     = "${lammps_mach}"
        steps.env.TARGET   = "${lammps_target}"
        steps.env.MODE     = "${lammps_mode}"
        steps.env.LMPFLAGS = '-sf off'
        steps.env.LMP_INC  = "-I/usr/include/hdf5/serial -DLAMMPS_${lammps_size} -DFFT_KISSFFT -DLAMMPS_GZIP -DLAMMPS_PNG -DLAMMPS_JPEG -Wall -Wextra -Wno-unused-result -Wno-unused-parameter -Wno-maybe-uninitialized"
        steps.env.JPG_LIB  = '-L/usr/lib/x86_64-linux-gnu/hdf5/serial/ -ljpeg -lpng -lz'

        if(lammps_mach != 'mpi') {
            steps.env.LMP_INC = "-I../../src/STUBS ${steps.env.LMP_INC}"
            steps.env.JPG_LIB = "-L../../src/STUBS/ ${steps.env.JPG_LIB} -lmpi_stubs"
        }

        steps.env.CC = c_compiler
        steps.env.CXX = cxx_compiler
        steps.env.OMPI_CC = c_compiler
        steps.env.OMPI_CXX = cxx_compiler
    }

    def build() {
        steps.sh 'ccache -M 5G'

        enable_packages()
        build_libraries()

        steps.stage('Compiling') {
            steps.sh '''#!/bin/bash -l
            make -j 8 -C lammps/src mode=${MODE} ${TARGET} MACH=${MACH} CC="${COMP}" LINK="${COMP}" LMP_INC="${LMP_INC}" JPG_LIB="${JPG_LIB}" LMPFLAGS="${LMPFLAGS}"
            '''
        }

        steps.sh 'ccache -s'
    }

    def post_actions() {
        steps.warnings consoleParsers: [[parserName: 'GNU Make + GNU C Compiler (gcc)']]
    }
}
