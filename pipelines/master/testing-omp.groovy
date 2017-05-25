import hudson.tasks.test.AbstractTestResultAction
import hudson.model.Actionable

@NonCPS
def hasFailedTests = { ->
    def testResultAction = currentBuild.rawBuild.getAction(AbstractTestResultAction.class)

    if (testResultAction != null) {
        def failed = testResultAction.getFailCount()
        return failed > 0
    }
    // no test results is always a failure
    return true
}

@NonCPS
def getTestSummary = { ->
    def testResultAction = currentBuild.rawBuild.getAction(AbstractTestResultAction.class)

    if (testResultAction != null) {
        def total = testResultAction.getTotalCount()
        def failed = testResultAction.getFailCount()
        def skipped = testResultAction.getSkipCount()
        def passed = total - failed - skipped
        return sprintf("Tests completed (%d passed, %d failed, %d skipped)", passed, failed, skipped)
    }
    return "No tests found"
}

node {
    def build_name = 'jenkins/testing'

    stage 'Checkout'
    git branch: 'master', credentialsId: 'lammps-jenkins', url: 'https://github.com/lammps/lammps.git'
    git_commit = sh(returnStdout: true, script: 'git rev-parse HEAD').trim()

//    step([$class: 'GitHubCommitStatusSetter', commitShaSource: [$class: 'ManuallyEnteredShaSource', sha: git_commit], contextSource: [$class: 'ManuallyEnteredCommitContextSource', context: build_name], reposSource: [$class: 'ManuallyEnteredRepositorySource', url: 'https://github.com/lammps/lammps.git'], statusResultSource: [$class: 'ConditionalStatusResultSource', results: [[$class: 'AnyBuildResult', message: 'building...', state: 'PENDING']]]])

    dir('lammps-testing') {
        git url: 'https://github.com/lammps/lammps-testing.git', credentialsId: 'lammps-jenkins', branch: 'master'
    }

    env.CCACHE_DIR= pwd() + '/.ccache'
    env.COMP     = 'mpicxx -fopenmp'
    env.MACH     = 'mpi'
    env.LMPFLAGS = '-sf omp'
    env.LMP_INC  = '-DLAMMPS_SMALLBIG -DFFT_KISSFFT -DLAMMPS_GZIP -DLAMMPS_PNG -DLAMMPS_JPEG -Wall -Wextra -Wno-unused-result -Wno-unused-parameter -Wno-maybe-uninitialized'
    env.JPG_LIB  = '-ljpeg -lpng -lz'

    env.CC = 'gcc'
    env.CXX = 'g++'
    env.OMPI_CC = 'gcc'
    env.OMPI_CXX = 'g++'

    env.LAMMPS_DIR = pwd()
    env.LAMMPS_MPI_MODE = 'openmpi'
    env.LAMMPS_BINARY = pwd() + '/src/lmp_' + env.MACH
    env.LAMMPS_TEST_MODES = 'omp'
    env.LAMMPS_POTENTIALS = pwd() + '/potentials'

    stage 'Setting up build environment'

    def envImage = docker.image('rbberger/lammps-testing:ubuntu_latest')

    try {
        docker.withRegistry('https://registry.hub.docker.com', 'docker-registry-login') {
            // ensure image is current
            envImage.pull()

            // use workaround (see https://issues.jenkins-ci.org/browse/JENKINS-34276)
            docker.image(envImage.imageName()).inside {
                sh 'ccache -C'
                sh 'ccache -M 5G'

                if (! fileExists('pyenv') ) {
                    sh 'virtualenv pyenv'
                }

                sh '''
                source pyenv/bin/activate
                pip install nose
                pip install nose2
                deactivate
                '''

                // clean up project directory
                sh '''
                make -C src clean-all
                '''

                stage 'Building libraries'

                sh '''
                make -C lib/atc -f Makefile.mpic++ clean
                make -C lib/colvars -f Makefile.g++ clean
                make -C lib/poems -f Makefile.g++ CXX="${COMP}" clean
                make -C lib/awpmd -f Makefile.mpicc CC="${COMP}" clean
                make -C lib/meam -f Makefile.gfortran CC=gcc F90=gfortran clean
                make -C lib/qmmm -f Makefile.gfortran clean
                make -C lib/reax -f Makefile.gfortran clean

                make -j 8 -C lib/atc -f Makefile.mpic++
                make -j 8 -C lib/colvars -f Makefile.g++ CXX="${COMP}"
                make -j 8 -C lib/poems -f Makefile.g++ CXX="${COMP}"
                make -j 8 -C lib/awpmd -f Makefile.mpicc CC="${COMP}"
                make -j 8 -C lib/meam -f Makefile.gfortran CC=gcc F90=gfortran
                make -j 8 -C lib/qmmm -f Makefile.gfortran
                make -j 8 -C lib/reax -f Makefile.gfortran
                '''

                sh '''
                cd lib/voronoi
                rm -rf build
                mkdir build
                python2 Install.py -g
                sed -i 's/CFLAGS=/CFLAGS=-fPIC /' voro++-0.4.6/config.mk
                python2 Install.py -b -l
                '''

                stage 'Enabling modules'

                sh '''
                make -C src yes-asphere
                make -C src yes-body
                make -C src yes-class2
                make -C src yes-colloid
                make -C src yes-compress
                make -C src yes-coreshell
                make -C src yes-dipole
                make -C src yes-fld
                make -C src yes-granular
                make -C src yes-kspace
                make -C src yes-manybody
                make -C src yes-mc
                make -C src yes-meam
                make -C src yes-misc
                make -C src yes-molecule
                make -C src yes-mpiio
                make -C src yes-opt
                make -C src yes-peri
                make -C src yes-poems
                make -C src yes-python
                make -C src yes-qeq
                make -C src yes-reax
                make -C src yes-replica
                make -C src yes-rigid
                make -C src yes-shock
                make -C src yes-snap
                make -C src yes-srd
                make -C src yes-voronoi
                make -C src yes-xtc
                make -C src yes-user-atc
                make -C src yes-user-awpmd
                make -C src yes-user-cg-cmm
                make -C src yes-user-colvars
                make -C src yes-user-diffraction
                make -C src yes-user-dpd
                make -C src yes-user-drude
                make -C src yes-user-eff
                make -C src yes-user-fep
                make -C src yes-user-lb
                make -C src yes-user-misc
                make -C src yes-user-molfile
                make -C src yes-user-phonon
                make -C src yes-user-qmmm
                make -C src yes-user-qtb
                make -C src yes-user-reaxc
                make -C src yes-user-sph
                make -C src yes-user-tally
                make -C src yes-user-smtbq
                make -C src yes-user-omp
                '''

                stage 'Compiling'
                sh 'make -j 8 -C src mode=shexe ${MACH} MPICMD="${MPICMD}" CC="${COMP}" LINK="${COMP}" LMP_INC="${LMP_INC}" JPG_LIB="${JPG_LIB}" TAG="${TAG}-$CC" LMPFLAGS="${LMPFLAGS}"'

                stage 'Testing'

                sh '''
                source pyenv/bin/activate
                cd python
                python install.py
                cd ..
                cd lammps-testing
                env
                python run_tests.py --processes 4 tests/test_commands.py tests/test_examples.py
                cd ..
                deactivate
                '''

                sh 'ccache -s'
            }
        }
    } catch (err) {
        echo "Caught: ${err}"
        currentBuild.result = 'FAILURE'
    }

    step([$class: 'WarningsPublisher', canComputeNew: false, consoleParsers: [[parserName: 'GNU Make + GNU C Compiler (gcc)']], defaultEncoding: '', excludePattern: '', healthy: '', includePattern: '', messagesPattern: '', unHealthy: ''])
    step([$class: 'AnalysisPublisher', canComputeNew: false, defaultEncoding: '', healthy: '', unHealthy: ''])
    junit 'lammps-testing/nosetests-*.xml'
    def summary = getTestSummary()

    if(hasFailedTests()) {
        // step([$class: 'GitHubCommitStatusSetter', commitShaSource: [$class: 'ManuallyEnteredShaSource', sha: git_commit], contextSource: [$class: 'ManuallyEnteredCommitContextSource', context: build_name], reposSource: [$class: 'ManuallyEnteredRepositorySource', url: 'https://github.com/lammps/lammps.git'], statusResultSource: [$class: 'ConditionalStatusResultSource', results: [[$class: 'AnyBuildResult', message: summary, state: 'FAILURE']]]])
    } else {
        // step([$class: 'GitHubCommitStatusSetter', commitShaSource: [$class: 'ManuallyEnteredShaSource', sha: git_commit], contextSource: [$class: 'ManuallyEnteredCommitContextSource', context: build_name], reposSource: [$class: 'ManuallyEnteredRepositorySource', url: 'https://github.com/lammps/lammps.git'], statusResultSource: [$class: 'ConditionalStatusResultSource', results: [[$class: 'AnyBuildResult', message: summary, state: 'SUCCESS']]]])
    }
}
