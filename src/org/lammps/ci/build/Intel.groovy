package org.lammps.ci.build

class Intel extends LegacyBuild {
    Intel(steps) {
        super('jenkins/intel', steps)
        compiler    = 'ccache mpiicpc -qopenmp'
        c_compiler  = 'ccache icc'
        cxx_compiler  = 'ccache icpc'
        lammps_mode = LAMMPS_MODE.shexe
        lammps_mach = 'mpi'
        lammps_size = LAMMPS_SIZES.SMALLBIG

        packages << 'yes-std'
        packages << 'no-lib'
        packages << 'yes-user-intel'
    }

    def configure() {
       super.configure()
       steps.env.LMP_INC="-g -mkl=sequential -DLAMMPS_MEMALIGN=64 -qno-offload -fno-alias -ansi-alias -restrict -xHost -O2 -fp-model fast=2 -no-prec-div -qoverride-limits -DFFT_MKL -DFFT_DOUBLE -DLAMMPS_GZIP -DLAMMPS_PNG -DLAMMPS_JPEG -DLAMMPS_${lammps_size} -Wall -w2"
       steps.env.JPG_LIB='-g -ltbbmalloc -ltbbmalloc_proxy -ljpeg -lpng -lz -mkl=sequential'
    }

    def post_actions() {
        steps.warnings consoleParsers: [[parserName: 'Intel C Compiler']]
    }
}
