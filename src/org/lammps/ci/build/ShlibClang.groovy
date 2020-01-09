package org.lammps.ci.build

class ShlibClang extends Shlib {
    ShlibClang(steps) {
        super('jenkins/shlib-clang', steps)
        compiler = 'clang++'
        c_compiler = 'clang'
        cxx_compiler = 'clang++'
    }
}
