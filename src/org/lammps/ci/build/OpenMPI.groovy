package org.lammps.ci.build

class OpenMPI extends LegacyBuild {
    OpenMPI(steps) {
        super('jenkins/openmpi', steps)
        compiler    = 'mpicxx'
        lammps_mode = LAMMPS_MODE.exe
        lammps_mach = 'mpi'
        lammps_size = LAMMPS_SIZES.BIGBIG

        packages << 'yes-all'
        packages << 'no-lib'
        packages << 'no-mpiio'
        packages << 'no-user-omp'
        packages << 'no-user-intel'
        packages << 'no-user-smd'
        packages << 'yes-user-molfile'
        packages << 'yes-compress'
        packages << 'yes-python'
        packages << 'yes-poems'
        packages << 'yes-user-colvars'
        packages << 'yes-user-awpmd'
        packages << 'yes-user-meamc'
        packages << 'yes-user-h5md'
        packages << 'yes-user-dpd'
        packages << 'yes-user-reaxc'
        packages << 'yes-user-meamc'
        packages << 'yes-mpiio'
        packages << 'yes-user-lb'
    }
}
