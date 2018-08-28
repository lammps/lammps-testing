node {
    def package_name = env.PACKAGE
    def build_name = "jenkins/cmake/master/${package_name}"
    def project_url = 'https://github.com/ellio167/lammps.git'
    def testing_project_url = 'https://github.com/lammps/lammps-testing.git'
    def docker_image_name = 'rbberger/lammps-testing:ubuntu_latest'
    def cmake_options = "-D PKG_${package_name}=on -D BUILD_MPI=on -D CMAKE_CXX_FLAGS=\"-O3 -Wall -Wextra -Wno-unused-result -Wno-maybe-uninitialized\""

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
                    if ( fileExists('pyenv') ) {
                        sh 'rm -rf pyenv'
                    }
                    sh 'virtualenv --python=$(which python) pyenv'

                    sh '''
                    source pyenv/bin/activate
                    pip install nose
                    deactivate
                    '''

                    stage('Configure') {
                        sh 'rm -rf build'
                        sh 'mkdir build'
                        sh '''
                        source pyenv2/bin/activate
                        cd build/
                        cd build && cmake $LAMMPS_CMAKE_OPTIONS ../lammps/cmake'
                        cd ..
                        deactivate
                        '''
                    }

                    stage('Compile') {
                        sh 'make -C build'
                    }

                    stage('Testing') {
                        sh '''
                        source pyenv/bin/activate
                        cd python
                        python install.py
                        cd ..
                        cd lammps-testing
                        env
                        python run_tests.py --processes 8 tests/test_package.py
                        cd ..
                        deactivate
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
