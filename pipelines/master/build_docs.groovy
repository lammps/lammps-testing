@Library(value='lammps_testing', changelog=false)
import org.lammps.ci.Utils

def project_url = 'https://github.com/lammps/lammps.git'
def set_github_status = true
def send_slack = true

def container = 'fedora32_mingw'
def launch_container = "singularity exec \$LAMMPS_CONTAINER_DIR/${container}.sif"

def lammps_branch = "master"

node('slow') {
    def utils = new Utils()
    env.LAMMPS_CONTAINER_DIR = "/mnt/lammps/containers"

    stage('Checkout') {
        dir('lammps') {
            commit = checkout([$class: 'GitSCM', branches: [[name: "*/${lammps_branch}"]], doGenerateSubmoduleConfigurations: false, extensions: [[$class: 'CloneOption', depth: 2, noTags: false, reference: '', shallow: true]], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'lammps-jenkins', url: project_url]]])
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
                    sh 'cd lammps/doc/html; tar cvzf ../lammps-docs.tar.gz *'
                }
                archiveArtifacts 'lammps/doc/lammps-docs.tar.gz'
            }

            stage('Generate PDF') {
                ansiColor('xterm') {
                    sh(label: "Build PDF on ${container}",
                       script: "${launch_container} make -C lammps/doc pdf")
                }
                archiveArtifacts 'lammps/doc/Manual.pdf'
            }

            stage('Check Spelling') {
                ansiColor('xterm') {
                    sh(label: "Run spellcheck on ${container}",
                       script: "${launch_container} make -C lammps/doc -j 8 spelling | tee spellcheck_build.log")
                }
            }
        }

        recordIssues enabledForFailure: true, filters: [excludeCategory('RemovedInSphinx20Warning|UserWarning'), excludeMessage('Duplicate declaration.*')], healthy: 1, qualityGates: [[threshold: 1, type: 'TOTAL', unstable: true]], tools: [groovyScript(parserId: 'sphinx', pattern: 'html_build.log'), groovyScript(parserId: 'spelling', pattern: 'spellcheck_build.log')], unhealthy: 2

        stage('Publish') {
            sshPublisher(publishers: [sshPublisherDesc(configName: 'docs.lammps.org', transfers: [sshTransfer(cleanRemote: false, excludes: '', execCommand: 'rm -rf /var/www/lammps/docs/*', execTimeout: 120000, flatten: false, makeEmptyDirs: false, noDefaultExcludes: false, patternSeparator: '[, ]+', remoteDirectory: '', remoteDirectorySDF: false, removePrefix: '', sourceFiles: ''), sshTransfer(cleanRemote: false, excludes: '', execCommand: 'tar xvzf /var/www/lammps/docs/lammps-docs.tar.gz -C /var/www/lammps/docs && rm /var/www/lammps/docs/lammps-docs.tar.gz', execTimeout: 120000, flatten: false, makeEmptyDirs: false, noDefaultExcludes: false, patternSeparator: '[, ]+', remoteDirectory: 'lammps/docs', remoteDirectorySDF: false, removePrefix: 'lammps/doc/', sourceFiles: 'lammps/doc/lammps-docs.tar.gz')], usePromotionTimestamp: false, useWorkspaceInPromotion: false, verbose: false)])
            sshPublisher(publishers: [sshPublisherDesc(configName: 'docs.lammps.org', transfers: [sshTransfer(cleanRemote: false, excludes: '', execCommand: '', execTimeout: 120000, flatten: false, makeEmptyDirs: false, noDefaultExcludes: false, patternSeparator: '[, ]+', remoteDirectory: 'lammps/docs/', remoteDirectorySDF: false, removePrefix: 'lammps/doc/', sourceFiles: 'lammps/doc/Manual.pdf')], usePromotionTimestamp: false, useWorkspaceInPromotion: false, verbose: false)])
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
