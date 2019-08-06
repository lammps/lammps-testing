package org.lammps.ci.build

class Testing extends LegacyTesting {
    Testing(steps) {
        super('jenkins/testing', steps)
        build.lammps_mach = 'serial'
        build.lammps_target = 'serial'
        build.lammps_size = LAMMPS_SIZES.SMALLSMALL

        build.packages << 'yes-all'
        build.packages << 'no-lib'
        build.packages << 'no-mpiio'
        build.packages << 'no-user-omp'
        build.packages << 'no-user-intel'
        build.packages << 'no-user-lb'
        build.packages << 'no-user-smd'
        build.packages << 'yes-user-molfile'
        build.packages << 'yes-compress'
        build.packages << 'yes-python'
        build.packages << 'yes-poems'
        build.packages << 'yes-voronoi'
        build.packages << 'yes-user-colvars'
        build.packages << 'yes-user-awpmd'
        build.packages << 'yes-user-meamc'
        build.packages << 'yes-user-h5md'
        build.packages << 'yes-user-dpd'
        build.packages << 'yes-user-reaxc'
        build.packages << 'yes-user-meamc'

        test_modes.serial = true
    }
}
