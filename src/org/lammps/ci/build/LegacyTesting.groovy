package org.lammps.ci.build
import hudson.tasks.test.AbstractTestResultAction
import hudson.model.Actionable

enum MPIMode {
    openmpi,
    mpich
}

class TestModes {
    def serial = false
    def parallel = false
    def omp = false
    def valgrind = false

    String toString() {
        def modes = []

        if(serial) {
            modes << 'serial'
        }

        if(parallel) {
            modes << 'parallel'
        }

        if(omp) {
            modes << 'omp'
        }

        if(valgrind) {
            modes << 'valgrind'
        }

        return modes.join(':')
    }
}

abstract class LegacyTesting implements Serializable {
    protected def name
    protected def steps
    LegacyBuild build

    TestModes test_modes
    MPIMode mpi_mode = MPIMode.openmpi

    def test_compile_flags = ''
    def test_link_flags = ''
    def message = ''

    LegacyTesting(name, steps) {
        this.name  = name
        this.steps = steps

        build = new LegacyBuild(name, steps)
        build.lammps_mode = LAMMPS_MODE.shexe

        test_modes = new TestModes()
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
        build.configure()

        steps.env.LMP_INC  = "${steps.env.LMP_INC} ${test_compile_flags}"
        steps.env.JPG_LIB  = "${steps.env.JPG_LIB} ${test_link_flags}"

        steps.env.LAMMPS_DIR = steps.pwd() + '/lammps'
        steps.env.LAMMPS_MPI_MODE = "${mpi_mode}"
        steps.env.LAMMPS_BINARY = steps.env.LAMMPS_DIR + '/src/lmp_' + steps.env.MACH
        steps.env.LAMMPS_TEST_MODES = "${test_modes}"
        steps.env.LAMMPS_POTENTIALS = steps.env.LAMMPS_DIR + '/potentials'
    }

    def build() {
        build.build()

        if (steps.fileExists('pyenv') ) {
            steps.sh 'rm -rf pyenv'
        }

        steps.sh '''
        virtualenv pyenv
        source pyenv/bin/activate
        pip install nose
        deactivate
        '''

        steps.stage('Testing') {
            steps.sh '''
            source pyenv/bin/activate
            cd lammps/python
            python install.py
            cd ../..
            cd lammps-testing
            python run_tests.py --processes 8 tests/test_commands.py tests/test_examples.py
            cd ..
            deactivate
            '''
        }
    }

    def post_actions() {
        steps.warnings consoleParsers: [[parserName: 'GNU Make + GNU C Compiler (gcc)']]
        steps.junit 'lammps-testing/nosetests-*.xml'
        message = '\n' + getTestSummary()

        if(hasFailedTests()) {
            steps.currentBuild.result = 'FAILURE'
        }
    }
}
