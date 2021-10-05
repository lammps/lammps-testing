@Library(value='lammps_testing', changelog=false)
import org.lammps.ci.Utils

def project_url = 'https://github.com/lammps/lammps.git'
def set_github_status = true
def send_slack = true

def lammps_branch = "master"
def potentials = '/mnt/lammps/downloads/potentials'
def lammps_testing_branch = "master"

node('ppc64le') {
    def utils = new Utils()

    stage('Checkout') {
        dir('lammps') {
            branch_name = "origin-pull/pull/${env.GITHUB_PR_NUMBER}/merge"
            refspec = "+refs/pull/${env.GITHUB_PR_NUMBER}/merge:refs/remotes/origin-pull/pull/${env.GITHUB_PR_NUMBER}/merge"
            checkout changelog: true, poll: true, scm: [$class: 'GitSCM', branches: [[name: branch_name]], doGenerateSubmoduleConfigurations: false, extensions: [[$class: 'CleanCheckout'], [$class: 'CloneOption', depth: 1, noTags: false, reference: '', shallow: true]], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'lammps-jenkins', name: 'origin-pull', refspec: refspec, url: project_url]]]
            sh "cp -f ${potentials}/* potentials/"
        }

        dir('lammps-testing') {
            checkout changelog: false, poll: false, scm: [$class: 'GitSCM', branches: [[name: "*/${lammps_testing_branch}"]], doGenerateSubmoduleConfigurations: false, extensions: [], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'lammps-jenkins', url: 'https://github.com/lammps/lammps-testing']]]
        }
    }

    if (set_github_status) {
        utils.setGitHubCommitStatus(project_url, env.JOB_NAME, env.GITHUB_PR_HEAD_SHA, 'building...', 'PENDING')
    }

    def err = null

    try {
        env.LAMMPS_DIR = "${env.WORKSPACE}/lammps"
        env.LAMMPS_TESTING_DIR = "${env.WORKSPACE}/lammps-testing"
        env.LAMMPS_CACHE_DIR = "${env.WORKSPACE}/cache"

        def build_script = "cmake_ibmxlc.sh"

        timeout(time: 2, unit: 'HOURS') {
            stage('Build') {
                ansiColor('xterm') {
                    sh(label: "Run build script",
                       script: "\$LAMMPS_TESTING_DIR/scripts/builds/${build_script}")
                }
            }
        }

        def tools = []

        if (build_script.contains("cmake")) {
            tools.add(cmake())
        }

        if (build_script.contains("_icc_")) {
            tools.add(intel())
        } else if (build_script.contains("_clang_")) {
            tools.add(clang())
        } else if (build_script.contains("_ibmxlc_")) {
            tools.add(xlc())
        } else {
            tools.add(gcc())
        }

        recordIssues(tools: tools)
    } catch (caughtErr) {
        err = caughtErr
        currentBuild.result = 'FAILURE'
    } finally {
        if (currentBuild.result == 'FAILURE') {
            if (set_github_status) {
                utils.setGitHubCommitStatus(project_url, env.JOB_NAME, env.GITHUB_PR_HEAD_SHA, 'build failed!', 'FAILURE')
            }
            if (send_slack) {
                slackSend color: 'danger', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} failed!"
            }
        } else {
            if (set_github_status) {
                utils.setGitHubCommitStatus(project_url, env.JOB_NAME, env.GITHUB_PR_HEAD_SHA, 'build successful!', 'SUCCESS')
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
