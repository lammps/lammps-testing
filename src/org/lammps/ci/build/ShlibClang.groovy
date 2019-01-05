package org.lammps.ci.build

class ShlibClang extends Shlib {
    ShlibClang(steps) {
        super(steps)
        name = 'jenkins/shlib-clang'
        compiler = 'clang++'
        c_compiler = 'clang'
        cxx_compiler = 'clang++'
    }
}
