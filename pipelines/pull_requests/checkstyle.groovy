@Library(value='lammps_testing', changelog=false)
import org.lammps.ci.Utils

def project_url = 'https://github.com/lammps/lammps.git'
def set_github_status = true
def send_slack = true

node('slow'){
    cleanWs()
    def utils = new Utils()
    env.LAMMPS_CONTAINER_DIR = "/mnt/lammps/containers"
    def container = "fedora32_mingw"
    def container_args = ""
    def launch_container = "singularity exec ${container_args} \$LAMMPS_CONTAINER_DIR/${container}.sif"

    stage('Checkout') {
        branch_name = "origin-pull/pull/${env.GITHUB_PR_NUMBER}/merge"
        refspec = "+refs/pull/${env.GITHUB_PR_NUMBER}/merge:refs/remotes/origin-pull/pull/${env.GITHUB_PR_NUMBER}/merge"
        checkout changelog: true, poll: true, scm: [$class: 'GitSCM', branches: [[name: branch_name]], doGenerateSubmoduleConfigurations: false, extensions: [[$class: 'CleanCheckout'], [$class: 'CloneOption', depth: 1, noTags: false, reference: '', shallow: true]], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'lammps-jenkins', name: 'origin-pull', refspec: refspec, url: project_url]]]
    }

    if (set_github_status) {
        utils.setGitHubCommitStatus(project_url, env.JOB_NAME, env.GITHUB_PR_HEAD_SHA, 'building...', 'PENDING')
    }

    try {
        stage('Whitespace') {
            if(fileExists('tools/coding_standard/whitespace.py')) {
                tee('whitespace.log') {
                    sh(label: "Check for whitespace errors",
                       script: "${launch_container} python3 tools/coding_standard/whitespace.py . || true")
                }
                recordIssues qualityGates: [[threshold: 1, type: 'TOTAL', unstable: true]], failOnError: true, tools: [groovyScript(parserId: 'whitespace', pattern: 'whitespace.log')]
            } else {
                echo 'Skipping'
            }
        }

        stage('File Permissions') {
            if(fileExists('tools/coding_standard/permissions.py')) {
                tee('permissions.log') {
                    sh(label: "Check file permissions",
                       script: "${launch_container} python3 tools/coding_standard/permissions.py . || true")
                }
                recordIssues qualityGates: [[threshold: 1, type: 'TOTAL', unstable: true]], failOnError: true, tools: [groovyScript(parserId: 'permissions', pattern: 'permissions.log')]
            } else {
                echo 'Skipping'
            }
        }

        stage('Homepage URLs') {
            if(fileExists('tools/coding_standard/homepage.py')) {
                tee('homepage.log') {
                    sh(label: "Check for old LAMMPS homepage URLs",
                       script: "${launch_container} python3 tools/coding_standard/homepage.py . || true")
                }
                recordIssues qualityGates: [[threshold: 1, type: 'TOTAL', unstable: true]], failOnError: true, tools: [groovyScript(parserId: 'homepage', pattern: 'homepage.log')]
            } else {
                echo 'Skipping'
            }
        }
    } catch(Exception e) {
        currentBuild.result = 'FAILURE'
    } finally {
        if (currentBuild.result == 'FAILURE') {
            if (set_github_status) {
                utils.setGitHubCommitStatus(project_url, env.JOB_NAME, env.GITHUB_PR_HEAD_SHA, 'Style issues detected!', 'FAILURE')
            }
            if (send_slack) {
                slackSend color: 'danger', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} failed!"
            }
        } else if (currentBuild.result == 'UNSTABLE') {
            if (set_github_status) {
                utils.setGitHubCommitStatus(project_url, env.JOB_NAME, env.GITHUB_PR_HEAD_SHA, 'Style issues detected!', 'SUCCESS')
            }
            if (send_slack) {
                slackSend color: 'warning', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} has style issues!"
            }
        } else {
            if (set_github_status) {
                utils.setGitHubCommitStatus(project_url, env.JOB_NAME, env.GITHUB_PR_HEAD_SHA, 'No warnings', 'SUCCESS')
            }
            if (send_slack) {
                slackSend color: 'good', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} succeeded!"
            }
        }
    }
}
