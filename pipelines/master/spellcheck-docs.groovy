node {
    def build_name = 'jenkins/spellcheck-docs'

    stage 'Checkout'
    git branch: 'master', credentialsId: 'lammps-jenkins', url: 'https://github.com/lammps/lammps.git'
    git_commit = sh(returnStdout: true, script: 'git rev-parse HEAD').trim()

    step([$class: 'GitHubCommitStatusSetter', commitShaSource: [$class: 'ManuallyEnteredShaSource', sha: git_commit], contextSource: [$class: 'ManuallyEnteredCommitContextSource', context: build_name], reposSource: [$class: 'ManuallyEnteredRepositorySource', url: 'https://github.com/lammps/lammps.git'], statusResultSource: [$class: 'ConditionalStatusResultSource', results: [[$class: 'AnyBuildResult', message: 'building...', state: 'PENDING']]]])


    stage 'Setting up build environment'

    def envImage = docker.image('rbberger/lammps-testing:ubuntu_latest')

    try {
        docker.withRegistry('https://registry.hub.docker.com', 'docker-registry-login') {
            // ensure image is current
            envImage.pull()


            // use workaround (see https://issues.jenkins-ci.org/browse/JENKINS-34276)
            docker.image(envImage.imageName()).inside {
                stage 'Check Spelling'
                sh 'make -C doc -j 8 spelling'
                sh 'cp -R /tmp/lammps-docs-ebe2ec56ed1854589319120dbd8bd0e816d30813/rst/ .'
            }

        }
        step([$class: 'GitHubCommitStatusSetter', commitShaSource: [$class: 'ManuallyEnteredShaSource', sha: git_commit], contextSource: [$class: 'ManuallyEnteredCommitContextSource', context: build_name], reposSource: [$class: 'ManuallyEnteredRepositorySource', url: 'https://github.com/lammps/lammps.git'], statusResultSource: [$class: 'ConditionalStatusResultSource', results: [[$class: 'AnyBuildResult', message: 'build successful!', state: 'SUCCESS']]]])

    } catch (err) {
        echo "Caught: ${err}"
        currentBuild.result = 'FAILURE'
        step([$class: 'GitHubCommitStatusSetter', commitShaSource: [$class: 'ManuallyEnteredShaSource', sha: git_commit], contextSource: [$class: 'ManuallyEnteredCommitContextSource', context: build_name], reposSource: [$class: 'ManuallyEnteredRepositorySource', url: 'https://github.com/lammps/lammps.git'], statusResultSource: [$class: 'ConditionalStatusResultSource', results: [[$class: 'AnyBuildResult', message: 'build !', state: 'FAILURE']]]])
    }

    warnings canComputeNew: false, canResolveRelativePaths: false, canRunOnFailed: true, categoriesPattern: '', consoleParsers: [[parserName: 'Sphinx Spelling Check']], defaultEncoding: '', excludePattern: '', failedTotalAll: '1', healthy: '0', includePattern: '', messagesPattern: '', unHealthy: '1', unstableTotalAll: '1'
    step([$class: 'AnalysisPublisher', canComputeNew: false, defaultEncoding: '', healthy: '', unHealthy: ''])

    if (currentBuild.result == 'FAILURE') {
        slackSend color: 'bad', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} failed!"
    } else {
        slackSend color: 'good', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} succeeded!"
    }
}
