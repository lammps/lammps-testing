package org.lammps.ci.build
import hudson.tasks.test.AbstractTestResultAction
import hudson.model.Actionable

abstract class CMakeTestingBuild implements Serializable {
    protected def name
    protected def steps

    def compiler = 'g++'
    def c_compiler = 'gcc'
    def cxx_compiler = 'g++'
    def cmake_options = []
    def message = ''

    TestModes test_modes
    MPIMode mpi_mode = MPIMode.openmpi

    def message = ''

    CMakeTestingBuild(name, steps) {
        this.name  = name
        this.steps = steps

        this.lammps_mode = LAMMPS_MODE.shexe
        this.test_modes = new TestModes()
    }

    def hasFailedTests() {
        def testResultAction = steps.currentBuild.rawBuild.getAction(AbstractTestResultAction.class)

        if (testResultAction != null) {
            return testResultAction.getFailCount() > 0
        }

        // no test results is always a failure
        return true
    }

    def getTestSummary() {
        def testResultAction = steps.currentBuild.rawBuild.getAction(AbstractTestResultAction.class)

        if (testResultAction != null) {
            def total = testResultAction.getTotalCount()
            def failed = testResultAction.getFailCount()
            def skipped = testResultAction.getSkipCount()
            def passed = total - failed - skipped
            return "Tests completed (${passed} passed, ${failed} failed, ${skipped} skipped)"
        }
        return "No tests found"
    }

    protected def configure() {
        steps.env.CCACHE_DIR = steps.pwd() + '/.ccache'
        steps.env.CC = c_compiler
        steps.env.CXX = cxx_compiler
        steps.env.OMPI_CC = c_compiler
        steps.env.OMPI_CXX = cxx_compiler

        steps.env.LAMMPS_DIR = steps.pwd() + '/lammps'
        steps.env.LAMMPS_MPI_MODE = "${mpi_mode}"
        steps.env.LAMMPS_BINARY = steps.pwd() + '/build/lmp'
        steps.env.LAMMPS_TEST_MODES = "${test_modes}"
        steps.env.LAMMPS_POTENTIALS = steps.env.LAMMPS_DIR + '/potentials'

        steps.stage('Configure') {
            steps.sh 'ccache -M 5G'
            steps.sh 'rm -rf build'
            steps.sh 'rm -rf pyenv'
            steps.sh 'mkdir build'
            steps.sh 'virtualenv pyenv'
            steps.sh '''
            source pyenv/bin/activate
            pip install nose
            deactivate
            '''
            steps.sh '#!/bin/bash -l\n source pyenv/bin/activate && cd build && cmake ' + cmake_options.join(' ') + ' -D CMAKE_INSTALL_PREFIX=$VIRTUAL_ENV ../lammps/cmake'
        }
    }

    def build() {
        steps.stage('Compiling') {
            steps.sh '''#!/bin/bash -l
            make -C build -j 8
            make -C build install
            '''
        }

        steps.sh 'ccache -s'


        steps.stage('Testing') {
            test()
        }
    }

    def test() {
        steps.env.LD_LIBRARY_PATH="$VIRTUAL_ENV/lib64:$LD_LIBRARY_PATH"
        steps.sh '''
        source pyenv/bin/activate
        cd lammps-testing
        python run_tests.py --processes 8 tests/test_commands.py tests/test_examples.py
        cd ..
        deactivate
        '''
    }

    def collect_reports() {
        steps.junit 'lammps-testing/nosetests-*.xml'
    }

    def post_actions() {
        steps.warnings consoleParsers: [[parserName: 'GNU Make + GNU C Compiler (gcc)']]
        collect_reports()
        message = '\n' + getTestSummary()

        if(hasFailedTests()) {
            steps.currentBuild.result = 'FAILURE'
        }
    }
}
