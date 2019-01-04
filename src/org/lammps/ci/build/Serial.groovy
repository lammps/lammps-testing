package org.lammps.ci.build

class Serial extends LegacyBuild {
    Serial(steps) {
        super('jenkins/serial', steps)
        lammps_mode = LAMMPS_MODE.exe
        lammps_mach = 'serial'
        lammps_size = LAMMPS_SIZES.SMALLSMALL
    }
}
