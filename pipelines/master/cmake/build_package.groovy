node {
    def build_name = "jenkins/cmake/master/{env.PACKAGE}"
    def project_url = 'https://github.com/lammps/lammps.git'
    def testing_project_url = 'https://github.com/lammps/lammps-testing.git'
    def docker_image_name = 'rbberger/lammps-testing:ubuntu_latest'
    def cmake_options = "-DENABLE_{env.PACKAGE}=on"

    stage('Checkout') {
        dir('lammps') {
            git branch: 'master', credentialsId: 'lammps-jenkins', url: project_url
            def git_commit = sh(returnStdout: true, script: 'git rev-parse HEAD').trim()
        }

        dir('lammps-testing') {
            git branch: 'master', credentialsId: 'lammps-jenkins', url: testing_project_url
        }
    }

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
                        sh 'cd build && cmake ../lammps/cmake ' + cmake_options
                    }

                    stage('Compile') {
                        sh 'make -C build'
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

    if (currentBuild.result == 'FAILURE') {
        slackSend color: 'bad', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} failed!"
    } else {
        slackSend color: 'good', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} succeeded!"
    }
}
