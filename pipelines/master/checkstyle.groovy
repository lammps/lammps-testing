@Library('lammps_testing',changelog=false)
import org.lammps.ci.Utils

def project_url = 'https://github.com/lammps/lammps.git'
def shallow_clone = true
def set_github_status = true
def send_slack = true
node('atlas2'){
    def utils = new Utils()
    
    stage('Checkout') {
        dir('lammps') {
            if(shallow_clone) {
              checkout([$class: 'GitSCM', branches: [[name: '*/master']], doGenerateSubmoduleConfigurations: false, extensions: [[$class: 'CloneOption', noTags: false, reference: '', shallow: true]], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'lammps-jenkins', url: project_url]]])
            } else {
              git branch: 'master', credentialsId: 'lammps-jenkins', url: project_url
            }
            git_commit = sh(returnStdout: true, script: 'git rev-parse HEAD').trim()
        }
    }
    
    if (set_github_status) {
        utils.setGitHubCommitStatus(project_url, "checkstyle", git_commit, 'building...', 'PENDING')
    }
    
    stage('Whitespace') {
        sh 'egrep -Rn "\\s+$"  lammps/src/ > whitespace.log || true'
        recordIssues qualityGates: [[threshold: 1, type: 'TOTAL', unstable: false]], filters: [includeFile('.*\\.cpp'), includeFile('.*\\.h'), excludeFile('lammps/src/USER-MGPT/*')], tools: [groovyScript(parserId: 'whitespace', pattern: 'whitespace.log')]
    }
    
    if (currentBuild.result == 'FAILURE') {
        if (set_github_status) {
            utils.setGitHubCommitStatus(project_url, env.JOB_NAME, git_commit, 'build failed!' + s.message, 'FAILURE')
        }
        if (send_slack) {
            slackSend color: 'bad', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} failed!" + s.message
        }
    } else {
        if (set_github_status) {
            utils.setGitHubCommitStatus(project_url, s.name, git_commit, 'build successful!' + s.message, 'SUCCESS')
        }
        if (send_slack) {
            slackSend color: 'good', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} succeeded!" + s.message
        }
    }
}
