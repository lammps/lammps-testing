node('atlas2') {
    cleanWs()

    env.LAMMPS_DIR = "${params.WORKSPACE_PARENT}/lammps"
    env.LAMMPS_TESTING_DIR = "${params.WORKSPACE_PARENT}/lammps-testing"

    def docker_registry = 'http://glados2.cst.temple.edu:5000'
    def docker_image_name = "${params.CONTAINER_IMAGE}"
    def docker_args = "-v ${params.WORKSPACE_PARENT}:${params.WORKSPACE_PARENT}"

    def envImage = docker.image(docker_image_name)
    def build_script = "${currentBuild.projectName}.sh"

    stage('Build') {
        docker.withRegistry(docker_registry) {
            envImage.pull()

            docker.image(envImage.imageName()).inside(docker_args) {
                timeout(time: 2, unit: 'HOURS') {
                    ansiColor('xterm') {
                        sh """#!/bin/bash -l
                        \$LAMMPS_TESTING_DIR/scripts/simple/${params.CONTAINER_NAME}/${build_script}
                        """
                    }
                }
            }
        }
    }

    warnings consoleParsers: [[parserName: 'GNU Make + GNU C Compiler (gcc)']]
}
