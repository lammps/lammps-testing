package org.lammps.ci.build

class Win32CrossSerialCMake extends CMakeMinGWCrossBuild {
    Win32CrossSerialCMake(steps) {
        super('jenkins/cmake/win32-serial', steps)
        bitness = '32'
        cmake_options = ['-C ../lammps/cmake/presets/mingw-cross.cmake',
                         '-D CMAKE_CXX_FLAGS="-Wall "']
    }
}
