@Library(value='lammps_testing', changelog=false)
import org.lammps.ci.Utils

def project_url = 'https://github.com/lammps/lammps.git'
def set_github_status = true
def send_slack = true
def lammps_branch = 'master'

node('atlas2'){
    def utils = new Utils()

    stage('Checkout') {
        dir('lammps') {
            commit = checkout([$class: 'GitSCM', branches: [[name: "*/${lammps_branch}"]], doGenerateSubmoduleConfigurations: false, extensions: [[$class: 'CloneOption', depth: 1, noTags: false, reference: '', shallow: true]], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'lammps-jenkins', url: project_url]]])
        }
    }

    if (set_github_status) {
        utils.setGitHubCommitStatus(project_url, env.JOB_NAME, commit.GIT_COMMIT, 'building...', 'PENDING')
    }

    stage('Whitespace') {
        sh 'egrep -Rn "\\s+$"  lammps/src/ > whitespace.log || true'
        recordIssues qualityGates: [[threshold: 1, type: 'TOTAL', unstable: false]], filters: [includeFile('.*\\.cpp'), includeFile('.*\\.h'), excludeFile('lammps/src/USER-MGPT/*')], tools: [groovyScript(parserId: 'whitespace', pattern: 'whitespace.log')]
    }

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
}
