package org.lammps.ci.build

class Shlib extends LegacyBuild {
    Shlib(steps) {
        super('jenkins/shlib', steps)
        lammps_mode = LAMMPS_MODE.shlib
        lammps_mach = 'serial'
        lammps_size = LAMMPS_SIZES.SMALLBIG
    }
}
