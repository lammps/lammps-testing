node('atlas2') {
    env.LAMMPS_DIR = "${params.WORKSPACE_PARENT}/lammps"
    env.LAMMPS_TESTING_DIR = "${params.WORKSPACE_PARENT}/lammps-testing"
    env.LAMMPS_CACHE_DIR = "${env.WORKSPACE}/cache"
    env.LAMMPS_CONTAINER_DIR = "/home/jenkins/containers"
    env.CCACHE_DIR = "${env.WORKSPACE}/${params.CCACHE_DIR}"

    if(!fileExists(env.CCACHE_DIR)) {
        sh(label: "Ensure CCACHE_DIR folder exists", script: "mkdir -p ${CCACHE_DIR}")
        if(fileExists(".ccache_latest")) {
            sh(label: "Seed CCACHE_DIR", script: "cp -R .ccache_latest/* ${env.CCACHE_DIR}/")
        }
    }

    def container = "${params.CONTAINER_IMAGE}"
    def container_args = "--nv -B ${params.WORKSPACE_PARENT}:${params.WORKSPACE_PARENT}"

    def build_script = "${currentBuild.projectName}/build.sh"
    def test_script = "${currentBuild.projectName}/test.sh"

    def launch_container = "singularity exec ${container_args} \$LAMMPS_CONTAINER_DIR/${container}.sif"

    timeout(time: 2, unit: 'HOURS') {
        stage('Build') {
            ansiColor('xterm') {
                sh(label: "Build test binary on ${container}",
                   script: "${launch_container} \$LAMMPS_TESTING_DIR/scripts/regression_tests/${build_script}")
            }
        }

        stage('Testing') {
            ansiColor('xterm') {
                sh(label: "Run regression_tests/${test_script} on ${container}",
                   script: "${launch_container} \$LAMMPS_TESTING_DIR/scripts/regression_tests/${test_script}")
            }
        }
    }

    recordIssues(tools: [gcc()])

    junit testDataPublishers: [[$class: 'AttachmentPublisher']], testResults: 'regression_*.xml'

    if (currentBuild.result == 'FAILURE') {
        slackSend channel: 'new-testing', color: 'bad', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} failed!"
    } else {
        slackSend channel: 'new-testing', color: 'good', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} succeeded!"
    }

    sh(label: "Save current CCACHE to seed future jobs", script: "rm -rf .ccache_latest && cp -R ${env.CCACHE_DIR} .ccache_latest")
}
