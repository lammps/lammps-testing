package org.lammps.ci.build

class Serial extends LegacyBuild {
    Serial(name, steps) {
        super(name, steps)
        lammps_mode = LAMMPS_MODE.exe
        lammps_mach = 'serial'
        lammps_target = 'serial'
        lammps_size = LAMMPS_SIZES.SMALLSMALL
        if(name == 'jenkins/serial/el7') {
            lammps_standard = LAMMPS_STANDARD.CXX98
        }

        packages << 'yes-all'
        packages << 'no-lib'
        packages << 'no-mpiio'
        packages << 'no-user-omp'
        packages << 'no-user-intel'
        packages << 'no-user-lb'
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
    }
}
