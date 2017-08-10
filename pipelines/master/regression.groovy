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
    def build_name = 'jenkins/regression'

    stage 'Checkout'
    git branch: 'master', credentialsId: 'lammps-jenkins', url: 'https://github.com/lammps/lammps.git'
    git_commit = sh(returnStdout: true, script: 'git rev-parse HEAD').trim()

    step([$class: 'GitHubCommitStatusSetter', commitShaSource: [$class: 'ManuallyEnteredShaSource', sha: git_commit], contextSource: [$class: 'ManuallyEnteredCommitContextSource', context: build_name], reposSource: [$class: 'ManuallyEnteredRepositorySource', url: 'https://github.com/lammps/lammps.git'], statusResultSource: [$class: 'ConditionalStatusResultSource', results: [[$class: 'AnyBuildResult', message: 'building...', state: 'PENDING']]]])

    dir('lammps-testing') {
        checkout([$class: 'GitSCM', branches: [[name: '*/master']], doGenerateSubmoduleConfigurations: false, extensions: [[$class: 'PathRestriction', excludedRegions: '', includedRegions: 'pipelines/master/regression.groovy']], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'lammps-jenkins', url: 'https://github.com/lammps/lammps-testing.git']]])
        sh 'git clean -x -f -d'
    }

    env.CCACHE_DIR= pwd() + '/.ccache'
    env.COMP     = 'mpicxx'
    env.MACH     = 'mpi'
    env.LMP_INC  = '-DLAMMPS_SMALLBIG -DLAMMPS_GZIP -DLAMMPS_PNG -DLAMMPS_JPEG -Wall -Wextra -Wno-unused-result -Wno-unused-parameter -Wno-maybe-uninitialized'
    env.JPG_LIB  = '-ljpeg -lpng -lz'

    env.CC = 'gcc'
    env.CXX = 'g++'
    env.OMPI_CC = 'gcc'
    env.OMPI_CXX = 'g++'

    env.LAMMPS_DIR = pwd()
    env.LAMMPS_MPI_MODE = 'openmpi'
    env.LAMMPS_BINARY = pwd() + '/src/lmp_' + env.MACH
    env.LAMMPS_TEST_MODES = 'serial'
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

                if (! fileExists('pyenv2') ) {
                    sh 'virtualenv --python=$(which python2) pyenv2'
                }

                sh '''
                source pyenv2/bin/activate
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
                make -C lib/atc -f Makefile.mpic++ EXTRAMAKE="Makefile.lammps.installed" clean
                make -C lib/colvars -f Makefile.g++ clean
                make -C lib/poems -f Makefile.g++ CXX="${COMP}" clean
                make -C lib/awpmd -f Makefile.mpicc CC="${COMP}" clean
                make -C lib/meam -f Makefile.gfortran CC=gcc F90=gfortran clean
                make -C lib/qmmm -f Makefile.gfortran clean
                make -C lib/reax -f Makefile.gfortran clean

                make -j 8 -C lib/atc EXTRAMAKE="Makefile.lammps.installed" -f Makefile.mpic++
                make -j 8 -C lib/colvars -f Makefile.g++ CXX="${COMP}"
                make -j 8 -C lib/poems -f Makefile.g++ CXX="${COMP}"
                make -j 8 -C lib/awpmd -f Makefile.mpicc CC="${COMP}"
                make -j 8 -C lib/meam -f Makefile.gfortran CC=gcc F90=gfortran
                make -j 8 -C lib/qmmm -f Makefile.gfortran
                make -j 8 -C lib/reax -f Makefile.gfortran
                '''

                sh '''
                cd lib/voronoi
                python2 Install.py -b
                cd ../..
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
                '''

                stage 'Compiling'
                sh 'make -j 8 -C src mode=shexe ${MACH} CC="${COMP}" LINK="${COMP}" LMP_INC="${LMP_INC}" JPG_LIB="${JPG_LIB}"'

                stage 'Testing'
                sh 'rm -rf lammps-testing/tests/examples/USER/eff'
                sh 'rm -rf lammps-testing/tests/examples/USER/misc/imd'
                sh 'rm -rf lammps-testing/tests/examples/USER/fep'
                sh 'rm -rf lammps-testing/tests/examples/USER/lb'
                sh 'rm -rf lammps-testing/tests/examples/HEAT'
                sh 'rm -rf lammps-testing/tests/examples/COUPLE'

                sh '''
                source pyenv2/bin/activate
                cd python
                python install.py
                cd ..
                rm *.out *.xml || true
                python2 lammps-testing/lammps_testing/regression.py 8 "mpiexec -np 8 ${LAMMPS_BINARY} -v CORES 8" lammps-testing/tests/examples -exclude kim gcmc mscg nemd prd tad neb VISCOSITY ASPHERE USER/mgpt USER/dpd/dpdrx-shardlow balance accelerate USER/atc USER/quip USER/misc/grem USER/misc/i-pi USER/misc/pimd USER/cg-cmm 2>&1 |tee test0.out
                python2 lammps-testing/lammps_testing/regression.py 8 "mpiexec -np 8 ${LAMMPS_BINARY} -partition 4x2 -v CORES 8" lammps-testing/tests/examples -only prd 2>&1 |tee test1.out
                deactivate
                '''
                sh 'python lammps-testing/lammps_testing/generate_regression_xml.py --test-dir $PWD/lammps-testing/tests/ --log-file test0.out --out-file regression_00.xml'
                sh 'python lammps-testing/lammps_testing/generate_regression_xml.py --test-dir $PWD/lammps-testing/tests/ --log-file test1.out --out-file regression_01.xml'
//                sh 'grep "*** no failures ***" test.out'

                sh 'ccache -s'
            }
        }
    } catch (err) {
        echo "Caught: ${err}"
        currentBuild.result = 'FAILURE'
    }

    step([$class: 'WarningsPublisher', canComputeNew: false, consoleParsers: [[parserName: 'GNU Make + GNU C Compiler (gcc)']], defaultEncoding: '', excludePattern: '', healthy: '', includePattern: '', messagesPattern: '', unHealthy: ''])
    step([$class: 'AnalysisPublisher', canComputeNew: false, defaultEncoding: '', healthy: '', unHealthy: ''])
    junit 'regression_*.xml'
    def summary = getTestSummary()

    if(hasFailedTests()) {
        step([$class: 'GitHubCommitStatusSetter', commitShaSource: [$class: 'ManuallyEnteredShaSource', sha: git_commit], contextSource: [$class: 'ManuallyEnteredCommitContextSource', context: build_name], reposSource: [$class: 'ManuallyEnteredRepositorySource', url: 'https://github.com/lammps/lammps.git'], statusResultSource: [$class: 'ConditionalStatusResultSource', results: [[$class: 'AnyBuildResult', message: summary, state: 'FAILURE']]]])
    } else {
        step([$class: 'GitHubCommitStatusSetter', commitShaSource: [$class: 'ManuallyEnteredShaSource', sha: git_commit], contextSource: [$class: 'ManuallyEnteredCommitContextSource', context: build_name], reposSource: [$class: 'ManuallyEnteredRepositorySource', url: 'https://github.com/lammps/lammps.git'], statusResultSource: [$class: 'ConditionalStatusResultSource', results: [[$class: 'AnyBuildResult', message: summary, state: 'SUCCESS']]]])
    }
}
