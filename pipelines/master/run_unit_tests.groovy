node('atlas2') {
    env.LAMMPS_DIR = "${env.WORKSPACE}"
    env.LAMMPS_TESTING_DIR = "${params.WORKSPACE_PARENT}/lammps-testing"
    env.LAMMPS_CACHE_DIR = "${env.WORKSPACE}/cache"
    env.LAMMPS_CONTAINER_DIR = "/mnt/lammps/containers"
    env.CCACHE_DIR = "${env.WORKSPACE}/${params.CCACHE_DIR}"
    env.GIT_COMMIT = params.GIT_COMMIT

    if(params.GITHUB_PR_NUMBER) {
        env.GITHUB_PR_NUMBER = params.GITHUB_PR_NUMBER
        env.CHANGE_ID = params.GITHUB_PR_NUMBER
    }

    def container = "${params.CONTAINER_IMAGE}"
    def container_args = "--nv -B ${params.WORKSPACE_PARENT}:${params.WORKSPACE_PARENT}"

    def build_script = "${currentBuild.projectName}/build.sh"
    def test_script = "${currentBuild.projectName}/test.sh"

    def launch_container = "singularity exec ${container_args} \$LAMMPS_CONTAINER_DIR/${container}.sif"

    stage('Copy LAMMPS sources') {
      sh "rsync -avht --exclude=.ccache --delete ${params.WORKSPACE_PARENT}/lammps/ ./"
    }

    timeout(time: 2, unit: 'HOURS') {
        stage('Build') {
            ansiColor('xterm') {
                sh(label: "Build test binary on ${container}",
                   script: "${launch_container} \$LAMMPS_TESTING_DIR/scripts/unit_tests/${build_script}")
            }
        }

        stage('Testing') {
            ansiColor('xterm') {
                sh(label: "Run unit_tests/${test_script} on ${container}",
                   script: "${launch_container} \$LAMMPS_TESTING_DIR/scripts/unit_tests/${test_script}")
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

    stage('Upload Results') {
        if (fileExists('build/coverage.xml')) {
            cobertura autoUpdateHealth: false, autoUpdateStability: false, coberturaReportFile: 'build/*coverage.xml', conditionalCoverageTargets: '70, 0, 0', failUnhealthy: false, failUnstable: false, lineCoverageTargets: '80, 0, 0', maxNumberOfBuilds: 0, methodCoverageTargets: '80, 0, 0', onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false

            sh 'curl -fLso codecov https://codecov.io/bash'

            def CODECOV_VERSION = sh script: 'grep -o \'VERSION="[0-9\\.]*"\' codecov | cut -d\'"\' -f2', returnStdout: true

            def valid_script = sh script: "for i in 1 256 512; do shasum -a \$i -c <(curl -s \"https://raw.githubusercontent.com/codecov/codecov-bash/${CODECOV_VERSION}/SHA\${i}SUM\" | grep -w \"codecov\"); done", returnStatus: true

            if (valid_script == 0) {
                withCredentials([string(credentialsId: 'codecov-token', variable: 'CODECOV_TOKEN')]) {
                    if (build_script.contains("gpu")) {
                        sh """#!/bin/bash
                        bash codecov -F gpu -f build/coverage.xml
                        """
                    } else {
                        sh """#!/bin/bash
                        bash codecov -f build/coverage.xml
                        """
                    }
                    if (fileExists('build/python_coverage.xml')) {
                         sh """#!/bin/bash
                         bash codecov -F python -f build/python_coverage.xml
                         """
                    }
                }
            } else {
                currentBuild.result = 'FAILURE'
            }
        }
    }

    if (currentBuild.result == 'FAILURE') {
        slackSend color: 'danger', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} failed!"
    } else if (currentBuild.result == 'UNSTABLE') {
        slackSend color: 'warning', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} has failed tests!"
    } else {
        slackSend color: 'good', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} succeeded!"
    }
}
