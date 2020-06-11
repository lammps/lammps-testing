node('atlas2') {
    env.LAMMPS_DIR = "${params.WORKSPACE_PARENT}/lammps"
    env.LAMMPS_TESTING_DIR = "${params.WORKSPACE_PARENT}/lammps-testing"
    env.LAMMPS_CONTAINER_DIR = "/home/jenkins/containers"
    env.CCACHE_DIR = "${env.WORKSPACE}/${params.CCACHE_DIR}"

    def container = "${params.CONTAINER_IMAGE}"
    def container_args = "--nv -B ${params.WORKSPACE_PARENT}:${params.WORKSPACE_PARENT}"

    def build_script = "${currentBuild.projectName}/build.sh"
    def test_script = "${currentBuild.projectName}/test.sh"

    def launch_container = "singularity exec ${container_args} \$LAMMPS_CONTAINER_DIR/${container}.sif"

    timeout(time: 2, unit: 'HOURS') {
        stage('Build') {
            ansiColor('xterm') {
                sh(label: "Build test binary on ${container}",
                   script: "${launch_container} \$LAMMPS_TESTING_DIR/scripts/run_tests/${build_script}")
            }
        }

        stage('Testing') {
            ansiColor('xterm') {
                sh(label: "Run run_tests/${test_script} on ${container}",
                   script: "${launch_container} \$LAMMPS_TESTING_DIR/scripts/run_tests/${test_script}")
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

    junit testDataPublishers: [[$class: 'AttachmentPublisher']], testResults: 'nosetests-*.xml'

    if (fileExists('build/coverage.xml')) {
        cobertura autoUpdateHealth: false, autoUpdateStability: false, coberturaReportFile: 'build/coverage.xml', conditionalCoverageTargets: '70, 0, 0', failUnhealthy: false, failUnstable: false, lineCoverageTargets: '80, 0, 0', maxNumberOfBuilds: 0, methodCoverageTargets: '80, 0, 0', onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false
    }

    if (currentBuild.result == 'FAILURE') {
        slackSend color: 'bad', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} failed!"
    } else {
        slackSend color: 'good', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} succeeded!"
    }
}
