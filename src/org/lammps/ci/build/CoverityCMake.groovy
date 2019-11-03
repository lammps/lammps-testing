package org.lammps.ci.build

class CoverityCMake implements Serializable {
    protected def name
    protected def steps
    def compiler = 'g++'
    def c_compiler = 'gcc'
    def cxx_compiler = 'g++'
    def python_executable = 'python'
    def cmake_options = ['-D CMAKE_CXX_FLAGS="-Wall -Wextra -Wno-unused-result -Wno-maybe-uninitialized"']
    def message = ''

    CoverityCMake(name, steps) {
        this.name  = name
        this.steps = steps
    }

    def pre_actions() {
        steps.withCredentials([steps.string(credentialsId: 'coverity-token', variable: 'COVERITY_TOKEN')]) {
            steps.sh "wget https://scan.coverity.com/download/linux64 --post-data \"token=$COVERITY_TOKEN&project=LAMMPS&md5=1\" -O coverity_tool.md5"
            if(!steps.fileExists('coverity_tool.tgz')) {
              steps.sh "wget https://scan.coverity.com/download/linux64 --post-data \"token=$COVERITY_TOKEN&project=LAMMPS\" -O coverity_tool.tgz"
            }
        }
    }

    def configure() {
        steps.env.CC = c_compiler
        steps.env.CXX = cxx_compiler
        steps.env.OMPI_CC = c_compiler
        steps.env.OMPI_CXX = cxx_compiler
        steps.stage('Configure') {
            steps.sh 'rm -rf build'
            steps.sh 'mkdir build'
            steps.sh '#!/bin/bash -l\n cd build && cmake ' + cmake_options.join(' ') + " -D PYTHON_EXECUTABLE=\$(which ${python_executable}) ../lammps/cmake"
        }
    }

    def build() {
        steps.stage('Compiling') {
            if (!steps.fileExists('cov-analysis-linux64-2019.03')) {
               steps.sh 'tar xvzf coverity_tool.tgz'
            }

            steps.sh 'export PATH=$PWD/cov-analysis-linux64-2019.03/bin:$PATH; cd build; cov-build --dir cov-int make -j 8'
        }
    }

    def post_actions() {
        steps.dir('lammps') {
            git_commit = steps.sh(returnStdout: true, script: 'git rev-parse HEAD').trim()
        }

        steps.stage('Upload') {
            steps.sh 'cd build; tar czvf LAMMPS.tgz cov-int'
            steps.archiveArtifacts 'build/LAMMPS.tgz'
            steps.withCredentials([steps.string(credentialsId: 'coverity-token', variable: 'COVERITY_TOKEN')]) {
                steps.sh "curl --form token=$COVERITY_TOKEN --form email=themechatronic@gmail.com  --form file=@build/LAMMPS.tgz --form version=\"${git_commit}\"   --form description=\"LAMMPS automated build\" https://scan.coverity.com/builds?project=LAMMPS"
            }
        }
    }
}
