package org.lammps.ci.build

class OpenMPIClang extends OpenMPI {
    OpenMPIClang(steps) {
        super('jenkins/openmpi-clang', steps)
        lammps_except = '-DLAMMPS_EXCEPTIONS'
        c_compiler = 'clang'
        cxx_compiler = 'clang++'
    }
}
