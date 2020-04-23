node('atlas2') {
    def docker_registry = 'http://glados2.cst.temple.edu:5000'
    def docker_image_name = 'lammps_testing:ubuntu_latest'
    def docker_args = ''
    def project_url = 'https://github.com/lammps/lammps.git'

    stage('Checkout') {
        dir('lammps') {
            commit = checkout([$class: 'GitSCM', branches: [[name: '*/master']], doGenerateSubmoduleConfigurations: false, extensions: [[$class: 'CloneOption', depth: 1, noTags: false, reference: '', shallow: true]], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'lammps-jenkins', url: 'https://github.com/lammps/lammps']]])
        }
    }

    def envImage = docker.image(docker_image_name)

    docker.withRegistry(docker_registry) {
        stage('Setting up build environment') {
            envImage.pull()
        }

        docker.image(envImage.imageName()).inside(docker_args) {
            timeout(time: 2, unit: 'HOURS') {
                steps.stage('Generate HTML') {
                    steps.sh 'make -C lammps/doc -j 8 html'
                    steps.sh 'cd lammps/doc/html; tar cvzf ../lammps-docs.tar.gz *'
                    steps.archiveArtifacts 'lammps/doc/lammps-docs.tar.gz'
                }

                steps.stage('Generate PDF') {
                    steps.sh 'make -C lammps/doc pdf'
                    steps.archiveArtifacts 'lammps/doc/Manual.pdf'
                }

                steps.stage('Check Spelling') {
                    steps.sh 'make -C lammps/doc -j 8 spelling'
                }
            }
        }
    }

    recordIssues filters: [excludeCategory('RemovedInSphinx20Warning|UserWarning'), excludeMessage('Duplicate declaration.*')], tools: [groovyScript('sphinx'), groovyScript('spelling')]
}
