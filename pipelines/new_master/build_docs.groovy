@Library(value='lammps_testing', changelog=false)
import org.lammps.ci.Utils

def project_url = 'https://github.com/lammps/lammps.git'
def set_github_status = true
def send_slack = true

def container = 'fedora32_mingw'
def launch_container = "singularity exec \$LAMMPS_CONTAINER_DIR/${container}.sif"

def lammps_branch = "master"

node('atlas2') {
    def utils = new Utils()
    env.LAMMPS_CONTAINER_DIR = "/home/jenkins/containers"

    stage('Checkout') {
        dir('lammps') {
            commit = checkout([$class: 'GitSCM', branches: [[name: "*/${lammps_branch}"]], doGenerateSubmoduleConfigurations: false, extensions: [[$class: 'CloneOption', depth: 1, noTags: false, reference: '', shallow: true]], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'lammps-jenkins', url: project_url]]])
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
                       script: "${launch_container} make -C lammps/doc -j 8 html")
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
                       script: "${launch_container} make -C lammps/doc -j 8 spelling")
                }
            }
        }

        warnings canComputeNew: false, canResolveRelativePaths: false, canRunOnFailed: true, categoriesPattern: 'RemovedInSphinx20Warning|UserWarning', consoleParsers: [[parserName: 'Sphinx Spelling Check'],[parserName: 'Sphinx Documentation Build']], defaultEncoding: '', excludePattern: '', failedTotalAll: '1', healthy: '0', includePattern: '', messagesPattern: 'Duplicate declaration.*', unHealthy: '1', unstableTotalAll: '1'
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
