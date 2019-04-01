package org.lammps.ci.build

class Win64CrossSerialCMake extends CMakeMinGWCrossBuild {
    Win64CrossSerialCMake(steps) {
        super('jenkins/cmake/win64-serial', steps)
        bitness = '64'
        cmake_options = ['-C ../lammps/cmake/presets/mingw-cross.cmake',
                         '-D CMAKE_CXX_FLAGS="-Wall "']
    }
}
