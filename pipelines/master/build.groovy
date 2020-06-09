node('atlas2') {
    env.LAMMPS_DIR = "${params.WORKSPACE_PARENT}/lammps"
    env.LAMMPS_TESTING_DIR = "${params.WORKSPACE_PARENT}/lammps-testing"
    env.LAMMPS_CONTAINER_DIR = "/home/jenkins/containers"
    env.CCACHE_DIR = "${env.WORKSPACE}/${params.CCACHE_DIR}"

    if(!fileExists(env.CCACHE_DIR)) {
        sh(label: "Ensure CCACHE_DIR folder exists", script: "mkdir -p ${CCACHE_DIR}")
        if(fileExists(".ccache_latest")) {
            sh(label: "Seed CCACHE_DIR", script: "rsync -ra .ccache_latest/ ${env.CCACHE_DIR}/")
        }
    }

    def container = "${params.CONTAINER_IMAGE}"
    def container_args = "--nv -B ${params.WORKSPACE_PARENT}:${params.WORKSPACE_PARENT}"

    def build_script = "${currentBuild.projectName}.sh"

    def launch_container = "singularity exec ${container_args} \$LAMMPS_CONTAINER_DIR/${container}.sif"

    timeout(time: 2, unit: 'HOURS') {
        stage('Build') {
            ansiColor('xterm') {
                sh(label: "Build test binary on ${container}",
                   script: "${launch_container} \$LAMMPS_TESTING_DIR/scripts/builds/${build_script}")
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

    if (currentBuild.result == 'FAILURE') {
        slackSend channel: 'new-testing', color: 'bad', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} failed!"
    } else {
        slackSend channel: 'new-testing', color: 'good', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} succeeded!"
    }

    sh(label: "Save current CCACHE to seed future jobs", script: "rm -rf .ccache_latest && rsync -ra ${env.CCACHE_DIR}/ .ccache_latest/")
}
