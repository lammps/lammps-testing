@Library(value='lammps_testing', changelog=false)
import org.lammps.ci.Utils

def project_url = 'https://github.com/lammps/lammps.git'
def set_github_status = false
def send_slack = false

def container = 'fedora32_mingw'
def launch_container = "singularity exec \$LAMMPS_CONTAINER_DIR/${container}.sif"

def lammps_branch = "unstable"

node('slow') {
    def utils = new Utils()
    env.LAMMPS_CONTAINER_DIR = "/mnt/lammps/containers"

    stage('Checkout') {
        dir('lammps') {
            commit = checkout([$class: 'GitSCM', branches: [[name: "*/${lammps_branch}"]], doGenerateSubmoduleConfigurations: false, extensions: [], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'lammps-jenkins', url: project_url]]])
            lammps_release_tag = sh(returnStdout: true, script: 'git describe --tags --abbrev=0 | cut -d_ -f2').trim()
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
                       script: "${launch_container} make -C lammps/doc clean-all")
                    sh(label: "Build HTML on ${container}",
                       script: "${launch_container} make -C lammps/doc -j 8 html | tee html_build.log")
                }
            }

            stage('Generate PDF') {
                ansiColor('xterm') {
                    sh(label: "Build PDF on ${container}",
                       script: "${launch_container} make -C lammps/doc pdf")
                }
            }

            stage('Generate Release') {
                ansiColor('xterm') {
                  if (fileExists('release.tar')) {
                    sh 'rm -f release.tar'
                  }

                  if (fileExists('release.tar.gz')) {
                    sh 'rm -f release.tar.gz'
                  }

                  dir('lammps') {
                    sh(label: "Generate initial release tarball",
                       script: "git archive --output=../release.tar --prefix=lammps-${lammps_release_tag}/ HEAD")
                  }

                  dir('lammps/doc') {
                    sh "tar -rf ../../release.tar --transform 's,^,lammps-${lammps_release_tag}/doc/,' html Manual.pdf"
                  }

                  sh 'gzip -9 release.tar'
                  archiveArtifacts 'release.tar.gz'
                }
            }
        }

        stage('Publish') {
            sshPublisher(publishers: [sshPublisherDesc(configName: 'docs.lammps.org', transfers: [sshTransfer(cleanRemote: false, excludes: '', execCommand: "mv /var/www/lammps/download/tars/release.tar.gz /var/www/lammps/download/tars/lammps-${lammps_release_tag}.tar.gz", execTimeout: 120000, flatten: false, makeEmptyDirs: false, noDefaultExcludes: false, patternSeparator: '[, ]+', remoteDirectory: '/var/www/lammps/download/tars/', remoteDirectorySDF: false, removePrefix: '', sourceFiles: 'release.tar.gz')], usePromotionTimestamp: false, useWorkspaceInPromotion: false, verbose: false)])
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
