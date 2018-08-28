node {
    def package_name = env.PACKAGE
    def build_name = "jenkins/cmake/master/${package_name}"
    def project_url = 'https://github.com/ellio167/lammps.git'
    def testing_project_url = 'https://github.com/lammps/lammps-testing.git'
    def docker_image_name = 'rbberger/lammps-testing:ubuntu_latest'
    def cmake_options = ['-D CMAKE_CXX_FLAGS="-Wall -Wextra -Wno-unused-result"',
                         "-D PKG_${package_name}=on"]

    stage('Checkout') {
        dir('lammps') {
            git branch: 'kim-v2-update', credentialsId: 'lammps-jenkins', url: project_url
            def git_commit = sh(returnStdout: true, script: 'git rev-parse HEAD').trim()
        }

        dir('lammps-testing') {
            git branch: 'master', credentialsId: 'lammps-jenkins', url: testing_project_url
        }
    }

    env.LAMMPS_DIR = pwd() + '/lammps'
    env.LAMMPS_MPI_MODE = 'openmpi'
    env.LAMMPS_BINARY = pwd() + '/build/lmp'
    env.LAMMPS_TEST_MODES = 'serial'
    env.LAMMPS_POTENTIALS = pwd() + '/lammps/potentials'
    env.LAMMPS_TEST_DIRS = env.PACKAGE_TEST_DIR
    env.LAMMPS_CMAKE_OPTIONS = cmake_options

    def utils = load 'lammps-testing/pipelines/master/cmake/utils.groovy'
    //utils.setGitHubCommitStatus(project_url, git_commit, 'building...', 'PENDING')

    stage('Setup') {
        def envImage = docker.image(docker_image_name)

        try {
            docker.withRegistry('https://registry.hub.docker.com', 'docker-registry-login') {
                // ensure image is current
                envImage.pull()

                // use workaround (see https://issues.jenkins-ci.org/browse/JENKINS-34276)
                docker.image(envImage.imageName()).inside {
                    stage('Configure') {
                        sh 'rm -rf build'
                        sh 'mkdir build'
                        sh 'cd build && cmake ' + cmake_options.join(' ') + " ../lammps/cmake"
                    }

                    stage('Compile') {
                        sh 'make -C build -j 8'
                    }

                    stage('Testing') {
                        if ( fileExists('pyenv') ) {
                            sh 'rm -rf lammps-testing/pyenv'
                        }

                        sh '''
                        cd lammps-testing
                        virtualenv pyenv
                        source pyenv/bin/activate
                        pip install nose
                        python run_tests.py --processes 8 tests/test_package.py
                        deactivate
                        cd ..
                        '''
                    }
                }
            }
            //utils.setGitHubCommitStatus(project_url, git_commit, 'build successful!', 'SUCCESS')

        } catch (err) {
            echo "Caught: ${err}"
            currentBuild.result = 'FAILURE'
            //utils.setGitHubCommitStatus(project_url, git_commit, 'build failed!', 'FAILURE')
        }
    }

    warnings consoleParsers: [[parserName: 'GNU Make + GNU C Compiler (gcc)']]
    junit 'lammps-testing/nosetests*.xml'

/*    if (currentBuild.result == 'FAILURE') {
        slackSend color: 'bad', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} failed!"
    } else {
        slackSend color: 'good', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} succeeded!"
    }
*/
}
