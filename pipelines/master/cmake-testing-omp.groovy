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
    def build_name = 'jenkins/cmake-testing-omp'
    def project_url = 'https://github.com/lammps/lammps.git'
    def testing_project_url = 'https://github.com/lammps/lammps-testing.git'
    def docker_image_name = 'rbberger/lammps-testing:ubuntu_latest'
    def cmake_options = ['-D BUILD_LIB=on',
                         '-D BUILD_SHARED_LIBS=on',
                         '-D BUILD_OMP=on',
                         '-D PKG_ASPHERE=yes',
                         '-D PKG_BODY=yes=yes',
                         '-D PKG_CLASS2=yes',
                         '-D PKG_COLLOID=yes',
                         '-D PKG_COMPRESS=yes',
                         '-D PKG_CORESHELL=yes',
                         '-D PKG_DIPOLE=yes',
                         '-D PKG_GRANULAR=yes',
                         '-D PKG_KSPACE=yes',
                         '-D PKG_MANYBODY=yes',
                         '-D PKG_MC=yes',
                         '-D PKG_MEAM=yes',
                         '-D PKG_MISC=yes',
                         '-D PKG_MOLECULE=yes',
                         '-D PKG_MPIIO=yes',
                         '-D PKG_OPT=yes',
                         '-D PKG_PERI=yes',
                         '-D PKG_POEMS=yes',
                         '-D PKG_PYTHON=yes',
                         '-D PKG_QEQ=yes',
                         '-D PKG_REAX=yes',
                         '-D PKG_REPLICA=yes',
                         '-D PKG_RIGID=yes',
                         '-D PKG_SHOCK=yes',
                         '-D PKG_SNAP=yes',
                         '-D PKG_SRD=yes',
                         '-D PKG_VORONOI=yes',
                         '-D DOWNLOAD_VORO=yes',
                         '-D PKG_USER-ATC=yes',
                         '-D PKG_USER-AWPMD=yes',
                         '-D PKG_USER-COLVARS=yes',
                         '-D PKG_USER-DIFFRACTION=yes',
                         '-D PKG_USER-DPD=yes',
                         '-D PKG_USER-DRUDE=yes',
                         '-D PKG_USER-EFF=yes',
                         '-D PKG_USER-FEP=yes',
                         '-D PKG_USER-LB=yes',
                         '-D PKG_USER-MISC=yes',
                         '-D PKG_USER-MOLFILE=yes',
                         '-D PKG_USER-PHONON=yes',
                         '-D PKG_USER-QTB=yes',
                         '-D PKG_USER-REAXC=yes',
                         '-D PKG_USER-SPH=yes',
                         '-D PKG_USER-TALLY=yes',
                         '-D PKG_USER-SMTBQ=yes',
                         '-D PKG_USER-OMP=yes',
                         '-D CMAKE_INSTALL_PREFIX=$VIRTUAL_ENV']

    stage('Checkout') {
        dir('lammps') {
            git branch: 'master', credentialsId: 'lammps-jenkins', url: project_url
            def git_commit = sh(returnStdout: true, script: 'git rev-parse HEAD').trim()
        }

        dir('lammps-testing') {
            checkout([$class: 'GitSCM', branches: [[name: '*/master']], doGenerateSubmoduleConfigurations: false, extensions: [[$class: 'PathRestriction', excludedRegions: '', includedRegions: 'pipelines/master/cmake-testing-omp.groovy']], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'lammps-jenkins', url: testing_project_url]]])
        }
    }

    def utils = load 'lammps-testing/pipelines/master/cmake/utils.groovy'
    utils.setGitHubCommitStatus(project_url, git_commit, 'building...', 'PENDING')

    env.LAMMPS_DIR = pwd() + '/lammps'
    env.LAMMPS_MPI_MODE = 'openmpi'
    env.LAMMPS_BINARY = pwd() + '/build/lmp'
    env.LAMMPS_TEST_MODES = 'omp'
    env.LAMMPS_POTENTIALS = pwd() + '/lammps/potentials'

    stage 'Setting up build environment'

    stage('Setup') {
        def envImage = docker.image(docker_image_name)

        try {
            docker.withRegistry('https://registry.hub.docker.com', 'docker-registry-login') {
                // ensure image is current
                envImage.pull()

                // use workaround (see https://issues.jenkins-ci.org/browse/JENKINS-34276)
                docker.image(envImage.imageName()).inside {
                    stage('Configure') {
                        sh 'rm -rf build pyenv'
                        sh 'mkdir build'

                        sh '''
                        virtualenv pyenv
                        source pyenv/bin/activate
                        pip install nose
                        deactivate
                        '''

                        sh 'source pyenv/bin/activate && cd build && cmake ' + cmake_options.join(' ') + " ../lammps/cmake"
                    }

                    stage('Compile') {
                        sh 'make -C build -j 8'
                        sh 'make -C build install'
                    }
                
                    stage('Testing') {
                        sh '''
                        source pyenv/bin/activate
                        cd lammps-testing
                        export LD_LIBRARY_PATH=$VIRTUAL_ENV/lib64:$LD_LIBRARY_PATH
                        python run_tests.py --processes 4 tests/test_commands.py tests/test_examples.py
                        cd ..
                        deactivate
                        '''
                    }
                }
            }
            utils.setGitHubCommitStatus(project_url, git_commit, 'build successful!', 'SUCCESS')

        } catch (err) {
            echo "Caught: ${err}"
            currentBuild.result = 'FAILURE'
        }
    }

    warnings consoleParsers: [[parserName: 'GNU Make + GNU C Compiler (gcc)']]
    junit 'lammps-testing/nosetests-*.xml'
    def summary = getTestSummary()

    if(hasFailedTests()) {
        utils.setGitHubCommitStatus(project_url, git_commit, summary, 'FAILURE')
    } else {
        utils.setGitHubCommitStatus(project_url, git_commit, summary, 'SUCCESS')
    }

    if (currentBuild.result == 'FAILURE') {
        slackSend color: 'bad', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} failed!\n" + summary
    } else {
        slackSend color: 'good', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} succeeded!\n" + summary
    }
}
