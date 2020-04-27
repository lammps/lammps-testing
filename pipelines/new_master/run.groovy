node('atlas2') {
    env.LAMMPS_DIR = "${params.WORKSPACE_PARENT}/lammps"
    env.LAMMPS_TESTING_DIR = "${params.WORKSPACE_PARENT}/lammps-testing"

    def docker_registry = 'http://glados2.cst.temple.edu:5000'
    def docker_image_name = "${params.CONTAINER_IMAGE}"
    def docker_args = "-v ${params.WORKSPACE_PARENT}:${params.WORKSPACE_PARENT}"

    def envImage = docker.image(docker_image_name)
    def build_script = "${currentBuild.projectName}/build.sh"
    def test_script = "${currentBuild.projectName}/test.sh"

    docker.withRegistry(docker_registry) {
        envImage.pull()

        docker.image(envImage.imageName()).inside(docker_args) {
            timeout(time: 2, unit: 'HOURS') {
                stage('Build') {
                    sh """#!/bin/bash -l
                    \$LAMMPS_TESTING_DIR/scripts/simple/runtests/${build_script}
                    """
                }

                stage('Testing') {
                    sh """#!/bin/bash -l
                    \$LAMMPS_TESTING_DIR/scripts/simple/runtests/${test_script}
                    """
                }
            }
        }
    }

    recordIssues(tools: [gcc()])

    junit keepLongStdio: true, testResults: 'nosetests-*.xml'

    cobertura autoUpdateHealth: false, autoUpdateStability: false, coberturaReportFile: 'build/coverage.xml', conditionalCoverageTargets: '70, 0, 0', failUnhealthy: false, failUnstable: false, lineCoverageTargets: '80, 0, 0', maxNumberOfBuilds: 0, methodCoverageTargets: '80, 0, 0', onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false

    if (currentBuild.result == 'FAILURE') {
        slackSend channel: 'new-testing', color: 'bad', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} failed!"
    } else {
        slackSend channel: 'new-testing', color: 'good', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} succeeded!"
    }
}
