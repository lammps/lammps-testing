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
                stage('Generate HTML') {
                    sh 'make -C lammps/doc -j 8 html'
                    sh 'cd lammps/doc/html; tar cvzf ../lammps-docs.tar.gz *'
                    archiveArtifacts 'lammps/doc/lammps-docs.tar.gz'
                }

                stage('Generate PDF') {
                    sh 'make -C lammps/doc pdf'
                    archiveArtifacts 'lammps/doc/Manual.pdf'
                }

                stage('Check Spelling') {
                    sh 'make -C lammps/doc -j 8 spelling'
                }
            }
        }
    }

    warnings canComputeNew: false, canResolveRelativePaths: false, canRunOnFailed: true, categoriesPattern: 'RemovedInSphinx20Warning|UserWarning', consoleParsers: [[parserName: 'Sphinx Spelling Check'],[parserName: 'Sphinx Documentation Build']], defaultEncoding: '', excludePattern: '', failedTotalAll: '1', healthy: '0', includePattern: '', messagesPattern: 'Duplicate declaration.*', unHealthy: '1', unstableTotalAll: '1'
}
