package org.lammps.ci.build

class CMakeMinGWCrossBuild implements Serializable {
    protected def name
    protected def steps

    def cmake_options = []
    def message = ''
    def bitness = '64'

    CMakeMinGWCrossBuild(name, steps) {
        this.name  = name
        this.steps = steps
    }

    def configure() {
        steps.env.CCACHE_DIR = steps.pwd() + '/.ccache'
        def folder = 'build' + bitness
        steps.stage('Configure') {
            steps.sh 'ccache -M 5G'
            steps.sh 'rm -rf ' + folder
            steps.sh 'mkdir ' + folder
            steps.sh '#!/bin/bash -l\n cd ' + folder + ' && mingw' + bitness + '-cmake ' + cmake_options.join(' ') + ' ../lammps/cmake'
        }
    }

    def build() {
        steps.stage('Compiling') {
            steps.sh '#!/bin/bash -l\n make -C build' + bitness + ' -j 8'
        }
        steps.sh 'ccache -s'
    }

    def post_actions() {
        steps.warnings consoleParsers: [[parserName: 'GNU Make + GNU C Compiler (gcc)']]
    }
}
