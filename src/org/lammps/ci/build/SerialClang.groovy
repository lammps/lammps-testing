package org.lammps.ci.build

class SerialClang extends Serial {
    SerialClang(steps) {
        super('jenkins/serial-clang', steps)
        compiler = 'clang++'
        c_compiler = 'clang'
        cxx_compiler = 'clang++'
    }
}
