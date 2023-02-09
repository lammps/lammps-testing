@Library(value='lammps_testing', changelog=false)
import org.lammps.ci.Utils

def project_url = 'https://github.com/lammps/website.git'
def set_github_status = false
def send_slack = true

def container = 'fedora34_mingw'
def launch_container = "singularity exec \$LAMMPS_CONTAINER_DIR/${container}.sif"

def website_branch = "main"

node('atlas2') {
    def utils = new Utils()
    env.LAMMPS_CONTAINER_DIR = "/mnt/lammps/containers"

    stage('Checkout') {
        dir('website') {
            commit = checkout([$class: 'GitSCM', branches: [[name: "*/${website_branch}"]], doGenerateSubmoduleConfigurations: false, extensions: [[$class: 'CloneOption', depth: 1, noTags: false, reference: '', shallow: true]], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'lammps-jenkins', url: project_url]]])
        }
    }

    if (set_github_status) {
        utils.setGitHubCommitStatus(project_url, env.JOB_NAME, commit.GIT_COMMIT, 'building...', 'PENDING')
    }

    def err = null

    try {
        timeout(time: 2, unit: 'HOURS') {
            stage('Generate HTML') {
                ansiColor('xterm') {
                    sh(label: "Clean directory",
                       script: "${launch_container} make -C website clean")
                    sh(label: "Build HTML on ${container}",
                       script: "${launch_container} sh -c 'set -o pipefail; make -C website all | tee html_build.log'")
                    sh 'cd website/html; tar cvzf ../../lammps-website.tar.gz *'
                }
            }
        }

        stage('Publish') {
            sshPublisher(publishers: [sshPublisherDesc(configName: 'docs.lammps.org', transfers: [sshTransfer(cleanRemote: false, excludes: '', execCommand: 'rm -rf /var/www/lammps/www/*', execTimeout: 120000, flatten: false, makeEmptyDirs: false, noDefaultExcludes: false, patternSeparator: '[, ]+', remoteDirectory: '', remoteDirectorySDF: false, removePrefix: '', sourceFiles: ''), sshTransfer(cleanRemote: false, excludes: '', execCommand: 'tar xvzf /var/www/lammps/www/lammps-website.tar.gz -C /var/www/lammps/www && rm /var/www/lammps/www/lammps-website.tar.gz', execTimeout: 120000, flatten: false, makeEmptyDirs: false, noDefaultExcludes: false, patternSeparator: '[, ]+', remoteDirectory: 'lammps/www', remoteDirectorySDF: false, removePrefix: '', sourceFiles: 'lammps-website.tar.gz')], usePromotionTimestamp: false, useWorkspaceInPromotion: false, verbose: false)])
        }
    } catch (caughtErr) {
        err = caughtErr
        currentBuild.result = 'FAILURE'
    } finally {
        if (currentBuild.result == 'FAILURE') {
            if (set_github_status) {
                utils.setGitHubCommitStatus(project_url, env.JOB_NAME, commit.GIT_COMMIT, 'build failed!', 'FAILURE')
            }
            if (send_slack) {
                slackSend color: 'bad', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} failed!"
            }
        } else {
            if (set_github_status) {
                utils.setGitHubCommitStatus(project_url, env.JOB_NAME, commit.GIT_COMMIT, 'build successful!', 'SUCCESS')
            }
            if (send_slack) {
                slackSend color: 'good', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} succeeded!"
            }
        }

        if(err) {
            throw err
        }
    }
}
