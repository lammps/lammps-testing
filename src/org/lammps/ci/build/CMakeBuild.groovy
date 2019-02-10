package org.lammps.ci.build

class CMakeBuild implements Serializable {
    protected def name
    protected def steps

    def compiler = 'g++'
    def c_compiler = 'gcc'
    def cxx_compiler = 'g++'
    def python_executable = 'python'
    def cmake_options = []
    def message = ''

    CMakeBuild(name, steps) {
        this.name  = name
        this.steps = steps
    }

    def configure() {
        steps.env.CCACHE_DIR = steps.pwd() + '/.ccache'
        steps.env.CC = c_compiler
        steps.env.CXX = cxx_compiler
        steps.env.OMPI_CC = c_compiler
        steps.env.OMPI_CXX = cxx_compiler
        steps.stage('Configure') {
            steps.sh 'ccache -M 5G'
            steps.sh 'rm -rf build'
            steps.sh 'mkdir build'
            steps.sh '#!/bin/bash -l\n cd build && cmake ' + cmake_options.join(' ') + " -D PYTHON_EXECUTABLE=\$(which ${python_executable}) ../lammps/cmake"
        }
    }

    def build() {

        steps.stage('Compiling') {
            steps.sh '''#!/bin/bash -l
            make -C build -j 8
            '''
        }

        steps.sh 'ccache -s'
    }

    def post_actions() {
        steps.warnings consoleParsers: [[parserName: 'GNU Make + GNU C Compiler (gcc)']]
    }
}
