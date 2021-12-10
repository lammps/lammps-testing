@Library(value='lammps_testing', changelog=false)
import org.lammps.ci.Utils

def project_url = 'https://github.com/lammps/lammps.git'
def set_github_status = false
def send_slack = true

def lammps_branch = "develop"
def lammps_testing_branch = "master"

node('wheatley2') {
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

        def build_script = "cmake_mpi_openmp_smallbig_clang_shared/build.sh"
        def test_script = "cmake_mpi_openmp_smallbig_clang_shared/test.sh"
        
        timeout(time: 2, unit: 'HOURS') {
        stage('Build') {
            ansiColor('xterm') {
                sh(label: "Build test binary",
                   script: "\$LAMMPS_TESTING_DIR/scripts/unit_tests/${build_script}")
            }
        }

        stage('Testing') {
            ansiColor('xterm') {
                sh(label: "Run unit_tests/${test_script}",
                   script: "\$LAMMPS_TESTING_DIR/scripts/unit_tests/${test_script}")
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

    xunit(thresholds: [failed(failureNewThreshold: '0', failureThreshold: '0', unstableNewThreshold: '0', unstableThreshold: '0')], tools: [CTest(deleteOutputFiles: true, failIfNotNew: true, pattern: 'build/Testing/**/Test.xml', skipNoTestFiles: false, stopProcessingIfError: true)])
    
    if (fileExists('build/coverage.xml')) {
        cobertura autoUpdateHealth: false, autoUpdateStability: false, coberturaReportFile: 'build/*coverage.xml', conditionalCoverageTargets: '70, 0, 0', failUnhealthy: false, failUnstable: false, lineCoverageTargets: '80, 0, 0', maxNumberOfBuilds: 0, methodCoverageTargets: '80, 0, 0', onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false
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
