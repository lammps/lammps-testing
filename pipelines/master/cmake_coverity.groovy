@Library(value='lammps_testing', changelog=false)
import org.lammps.ci.Utils

def project_url = 'https://github.com/lammps/lammps.git'
def set_github_status = false
def send_slack = true

def lammps_branch = "master"
def lammps_testing_branch = "master"

node('atlas2') {
    def utils = new Utils()

    stage('Checkout') {
        dir('lammps') {
            commit = checkout([$class: 'GitSCM', branches: [[name: "*/${lammps_branch}"]], doGenerateSubmoduleConfigurations: false, extensions: [[$class: 'CloneOption', depth: 1, noTags: false, reference: '', shallow: true]], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'lammps-jenkins', url: 'https://github.com/lammps/lammps']]])
        }

        dir('lammps-testing') {
            checkout changelog: false, poll: false, scm: [$class: 'GitSCM', branches: [[name: "*/${lammps_testing_branch}"]], doGenerateSubmoduleConfigurations: false, extensions: [], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'lammps-jenkins', url: 'https://github.com/lammps/lammps-testing']]]
        }
    }

    if (set_github_status) {
        utils.setGitHubCommitStatus(project_url, env.JOB_NAME, commit.GIT_COMMIT, 'building...', 'PENDING')
    }

    def err = null

    try {
        env.LAMMPS_DIR = "${env.WORKSPACE}/lammps"
        env.LAMMPS_TESTING_DIR = "${env.WORKSPACE}/lammps-testing"
        env.LAMMPS_CACHE_DIR = "${env.WORKSPACE}/cache"
        env.LAMMPS_CONTAINER_DIR = "/home/jenkins/containers"

        def container = "ubuntu20.04"
        def container_args = "--nv -B /opt/coverity:/opt/coverity"

        def build_script = "cmake_coverity.sh"

        def launch_container = "singularity exec ${container_args} \$LAMMPS_CONTAINER_DIR/${container}.sif"

        timeout(time: 2, unit: 'HOURS') {
            stage('Build') {
                ansiColor('xterm') {
                    sh(label: "Run static code analysis in ${container}",
                       script: "${launch_container} \$LAMMPS_TESTING_DIR/scripts/static_analysis/${build_script}")
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
                utils.setGitHubCommitStatus(project_url, env.JOB_NAME, commit.GIT_COMMIT, 'build failed!', 'FAILURE')
            }
            if (send_slack) {
                slackSend color: 'danger', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} failed!"
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
