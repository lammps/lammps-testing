def selector = 'multicore'

if (currentBuild.projectName.contains("_icc_") || currentBuild.projectName.contains("_oneapi_") || currentBuild.projectName.contains("_kokkos_")) {
  // run on latest gen hardware
  selector = 'atlas2'
}

node(selector) {
    env.LAMMPS_DIR = "${params.WORKSPACE_PARENT}/lammps"
    env.LAMMPS_TESTING_DIR = "${params.WORKSPACE_PARENT}/lammps-testing"
    env.LAMMPS_CONTAINER_DIR = "/mnt/lammps/containers"
    env.CCACHE_DIR = "${env.WORKSPACE}/${params.CCACHE_DIR}"
    env.CCACHE_STORAGE_DIR = "${params.WORKSPACE_PARENT}/caches"

    def container = "${params.CONTAINER_IMAGE}"
    def container_args = "--nv -B ${params.WORKSPACE_PARENT}:${params.WORKSPACE_PARENT}"

    def build_script = "${currentBuild.projectName}.sh"

    def launch_container = "singularity exec ${container_args} \$LAMMPS_CONTAINER_DIR/${container}.sif"

    if (!fileExists('.ccache') && fileExists("${env.CCACHE_STORAGE_DIR}/${env.JOB_NAME}/ccache.tar.gz")) {
        echo 'Restoring ccache...'
        sh 'tar xzf $CCACHE_STORAGE_DIR/$JOB_NAME/ccache.tar.gz'
    }

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

    if (build_script.contains("_icc_") || build_script.contains("_oneapi_")) {
        tools.add(intel())
    } else if (build_script.contains("_clang_")) {
        tools.add(clang())
    } else {
        tools.add(gcc())
    }

    recordIssues(tools: tools)

    if (fileExists('pyenv/lammps.tgz')) {
        archiveArtifacts artifacts: 'pyenv/lammps.tgz', fingerprint: true, followSymlinks: false
    }

    if (!fileExists("${env.CCACHE_STORAGE_DIR}/${env.JOB_NAME}/ccache.tar.gz")) {
        sh '''cd $CCACHE_DIR/..
        mkdir -p $CCACHE_STORAGE_DIR/$JOB_NAME
        tar czf $CCACHE_STORAGE_DIR/$JOB_NAME/ccache.tar.gz  .ccache
        '''
    }

    if (currentBuild.result == 'FAILURE') {
        slackSend color: 'bad', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} failed!"
    } else {
        slackSend color: 'good', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} succeeded!"
    }
}
