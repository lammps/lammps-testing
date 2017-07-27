node {
    def build_name = 'jenkins/build-docs'

    stage 'Checkout'
    git branch: 'master', credentialsId: 'lammps-jenkins', url: 'https://github.com/lammps/lammps-git-tutorial.git'
    git_commit = sh(returnStdout: true, script: 'git rev-parse HEAD').trim()

    step([$class: 'GitHubCommitStatusSetter', commitShaSource: [$class: 'ManuallyEnteredShaSource', sha: git_commit], contextSource: [$class: 'ManuallyEnteredCommitContextSource', context: build_name], reposSource: [$class: 'ManuallyEnteredRepositorySource', url: 'https://github.com/lammps/lammps-git-tutorial.git'], statusResultSource: [$class: 'ConditionalStatusResultSource', results: [[$class: 'AnyBuildResult', message: 'building...', state: 'PENDING']]]])


    stage 'Setting up build environment'

    def envImage = docker.image('rbberger/lammps-testing:ubuntu_latest')

    try {
        docker.withRegistry('https://registry.hub.docker.com', 'docker-registry-login') {
            // ensure image is current
            envImage.pull()


            // use workaround (see https://issues.jenkins-ci.org/browse/JENKINS-34276)
            docker.image(envImage.imageName()).inside {
                stage 'Generate HTML'
                sh 'make -C doc -j 8 html'

                sh 'cd doc/html; tar cvzf ../lammps-docs.tar.gz *'

                archiveArtifacts 'doc/lammps-docs.tar.gz'

                stage 'Generate PDF'
                sh 'make -C doc pdf'
                archiveArtifacts 'doc/Manual.pdf'
            }

        }
        step([$class: 'GitHubCommitStatusSetter', commitShaSource: [$class: 'ManuallyEnteredShaSource', sha: git_commit], contextSource: [$class: 'ManuallyEnteredCommitContextSource', context: build_name], reposSource: [$class: 'ManuallyEnteredRepositorySource', url: 'https://github.com/lammps/lammps-git-tutorial.git'], statusResultSource: [$class: 'ConditionalStatusResultSource', results: [[$class: 'AnyBuildResult', message: 'build successful!', state: 'SUCCESS']]]])

    } catch (err) {
        echo "Caught: ${err}"
        currentBuild.result = 'FAILURE'
        step([$class: 'GitHubCommitStatusSetter', commitShaSource: [$class: 'ManuallyEnteredShaSource', sha: git_commit], contextSource: [$class: 'ManuallyEnteredCommitContextSource', context: build_name], reposSource: [$class: 'ManuallyEnteredRepositorySource', url: 'https://github.com/lammps/lammps-git-tutorial.git'], statusResultSource: [$class: 'ConditionalStatusResultSource', results: [[$class: 'AnyBuildResult', message: 'build !', state: 'FAILURE']]]])
    }

    step([$class: 'WarningsPublisher', canComputeNew: false, canResolveRelativePaths: false, consoleParsers: [[parserName: 'Sphinx Documentation Build']], defaultEncoding: '', excludePattern: '', healthy: '', includePattern: '', messagesPattern: '', unHealthy: ''])
    step([$class: 'AnalysisPublisher', canComputeNew: false, defaultEncoding: '', healthy: '', unHealthy: ''])

    if (currentBuild.result == 'FAILURE') {
        slackSend channel: '#lammps-workshop', color: 'bad', message: "(WORKSHOP) Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} failed!"
    } else {
        slackSend channel: '#lammps-workshop', color: 'good', message: "(WORKSHOP) Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} succeeded!"
    }
}
