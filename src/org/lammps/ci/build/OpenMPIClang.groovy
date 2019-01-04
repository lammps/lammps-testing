package org.lammps.ci.build

class OpenMPIClang extends OpenMPI {
    OpenMPIClang(steps) {
        super(steps)
        name = 'jenkins/openmpi-clang'
        c_compiler = 'clang'
        cxx_compiler = 'clang++'
    }
}
