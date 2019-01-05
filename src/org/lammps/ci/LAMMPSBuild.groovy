package org.lammps.ci
import org.lammps.ci.build.Serial
import org.lammps.ci.build.Shlib
import org.lammps.ci.build.OpenMPI
import org.lammps.ci.build.SerialClang
import org.lammps.ci.build.ShlibClang
import org.lammps.ci.build.OpenMPIClang
import org.lammps.ci.build.Documentation


def regular_build(build_name) {
    def docker_registry = 'http://glados.cst.temple.edu:5000'
    def docker_image_name = 'lammps_testing:ubuntu_latest'
    def project_url = 'https://github.com/lammps/lammps.git'

    switch(build_name) {
        case 'new-serial':
            s = new Serial(this)
            break
        case 'new-shlib':
            s = new Shlib(this)
            break
        case 'new-openmpi':
            s = new OpenMPI(this)
            break
        case 'new-serial-clang':
            s = new SerialClang(this)
            break
        case 'new-shlib-clang':
            s = new ShlibClang(this)
            break
        case 'new-openmpi-clang':
            s = new OpenMPIClang(this)
            break
        case 'new-build-docs':
            s = new Documentation(this)
            break
        default:
            currentBuild.result = 'FAILURE'
            echo 'unknown build_name'
            return
    }

    stage('Checkout') {
        dir('lammps') {
            git branch: 'master', credentialsId: 'lammps-jenkins', url: project_url
            git_commit = sh(returnStdout: true, script: 'git rev-parse HEAD').trim()
        }
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

    s.post_actions()

    if (currentBuild.result == 'FAILURE') {
        slackSend color: 'bad', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} failed!"
    } else {
        slackSend color: 'good', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} succeeded!"
    }
}

def pull_request(build_name) {
    def docker_registry = 'http://glados.cst.temple.edu:5000'
    def docker_image_name = 'lammps_testing:ubuntu_latest'
    def project_url = 'https://github.com/lammps/lammps.git'
    //def testing_project_url = 'https://github.com/lammps/lammps-testing.git'

    switch(build_name) {
        case 'new-serial':
            s = new Serial(this)
            break
        case 'new-shlib':
            s = new Shlib(this)
            break
        case 'new-openmpi':
            s = new OpenMPI(this)
            break
        case 'new-serial-clang':
            s = new SerialClang(this)
            break
        case 'new-shlib-clang':
            s = new ShlibClang(this)
            break
        case 'new-openmpi-clang':
            s = new OpenMPIClang(this)
            break
        case 'new-build-docs':
            s = new Documentation(this)
            break
        default:
            currentBuild.result = 'FAILURE'
            echo 'unknown build_name'
            return
    }

    stage('Checkout') {
        dir('lammps') {
            branch_name = "origin-pull/pull/${env.GITHUB_PR_NUMBER}/${env.GITHUB_PR_COND_REF}"
            refspec = "+refs/pull/${env.GITHUB_PR_NUMBER}/merge:refs/remotes/origin-pull/pull/${env.GITHUB_PR_NUMBER}/${env.GITHUB_PR_COND_REF}"
            checkout([$class: 'GitSCM', branches: [[name: branch_name]], doGenerateSubmoduleConfigurations: false, extensions: [[$class: 'CleanCheckout']], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'lammps-jenkins', name: 'origin-pull', refspec: refspec, url: project_url]]])
        }

    /*    dir('lammps-testing') {
            git branch: 'master', credentialsId: 'lammps-jenkins', url: testing_project_url
        }*/
    }

    gitHubPRStatus githubPRMessage('${GITHUB_PR_COND_REF} run started')

    def envImage = docker.image(docker_image_name)

    try {
        docker.withRegistry(docker_registry) {
            stage('Setup Environment') {
                // ensure image is current
                envImage.pull()
            }

            // use workaround (see https://issues.jenkins-ci.org/browse/JENKINS-34276)
            docker.image(envImage.imageName()).inside {
                s.build()
            }
        }
        currentBuild.result = 'SUCCESS'
    } catch (err) {
        echo "Caught: ${err}"
        currentBuild.result = 'FAILURE'
    }

    githubPRStatusPublisher statusMsg: githubPRMessage('${GITHUB_PR_COND_REF} run ended'), unstableAs: 'SUCCESS'

    s.post_actions()

    if (currentBuild.result == 'FAILURE') {
        slackSend color: 'bad', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} failed!"
    } else {
        slackSend color: 'good', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} succeeded!"
    }
}

return this
