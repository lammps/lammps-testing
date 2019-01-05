package org.lammps.ci.build

class SerialClang extends Serial {
    SerialClang(steps) {
        super(steps)
        name = 'jenkins/serial-clang'
        compiler = 'clang++'
        c_compiler = 'clang'
        cxx_compiler = 'clang++'
    }
}
