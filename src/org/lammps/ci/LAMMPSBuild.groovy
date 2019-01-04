package org.lammps.ci
import org.lammps.ci.build.Serial

def regular_build(build_name) {
    def docker_registry = 'http://glados.cst.temple.edu:5000'
    def docker_image_name = 'lammps_testing:ubuntu_latest'
    def project_url = 'https://github.com/lammps/lammps.git'

    node {
        switch(build_name) {
            case 'serial':
                s = new Serial(this)
                break
        }

        stage('Checkout') {
            git branch: 'master', credentialsId: 'lammps-jenkins', url: project_url
            git_commit = sh(returnStdout: true, script: 'git rev-parse HEAD').trim()
        }

        def utils = new Utils()

        utils.setGitHubCommitStatus(project_url, s.name, git_commit, 'building...', 'PENDING')

        def envImage = docker.image(docker_image_name)

        try {
            docker.withRegistry(docker_registry) {
                stage('Setting up build environment') {
                    // ensure image is current
                    envImage.pull()
                }

                // use workaround (see https://issues.jenkins-ci.org/browse/JENKINS-34276)
                docker.image(envImage.imageName()).inside {
                    s.build()
                }
            }

            utils.setGitHubCommitStatus(project_url, s.name, git_commit, 'build successful!', 'SUCCESS')
        } catch (err) {
            echo "Caught: ${err}"
            currentBuild.result = 'FAILURE'
            utils.setGitHubCommitStatus(project_url, s.name, git_commit, 'build failed!', 'FAILURE')
        }

        warnings consoleParsers: [[parserName: 'GNU Make + GNU C Compiler (gcc)']]

        if (currentBuild.result == 'FAILURE') {
            slackSend color: 'bad', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} failed!"
        } else {
            slackSend color: 'good', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} succeeded!"
        }
    }
}

return this
