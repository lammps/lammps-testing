node('atlas2') {
    def docker_image_name = "lammps:${env.JOB_BASE_NAME}"
    def dockerfile = "${params.WORKSPACE_PARENT}/lammps-packages/docker/${env.JOB_BASE_NAME}/Dockerfile"

    stage('Build') {
        result = docker.build(docker_image_name, "-f ${dockerfile} ${params.WORKSPACE_PARENT}")
    }

    if (currentBuild.result == 'FAILURE') {
        slackSend color: 'bad', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} failed!"
    } else {
        slackSend color: 'good', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} succeeded!"
    }
}
