node {
    def build_name = 'jenkins/build-docs'
    def merge_branch = 'origin-pull/pull/' + env.GITHUB_PR_NUMBER + '/merge'
    def merge_refspec = '+refs/pull/' + env.GITHUB_PR_NUMBER + '/merge:refs/remotes/origin-pull/pull/' + env.GITHUB_PR_NUMBER +'/merge'

   stage 'Checkout'
   checkout([$class: 'GitSCM', branches: [[name: merge_branch]], doGenerateSubmoduleConfigurations: false, extensions: [], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'lammps-jenkins', name: 'origin-pull', refspec: merge_refspec, url: 'https://github.com/lammps/lammps-git-tutorial']]])
    git_commit = sh(returnStdout: true, script: 'git rev-parse HEAD').trim()

    step([$class: 'GitHubPRStatusBuilder', statusMessage: [content: env.GITHUB_PR_COND_REF + ' run started']])


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
    } catch (err) {
        echo "Caught: ${err}"
        currentBuild.result = 'FAILURE'
    }
    step([$class: 'GitHubPRBuildStatusPublisher', buildMessage: [failureMsg: [content: 'Can\'t set status; build failed.'], successMsg: [content: 'Can\'t set status; build succeeded.']], statusMsg: [content: env.GITHUB_PR_COND_REF + ' run ended'], unstableAs: 'FAILURE'])

    step([$class: 'WarningsPublisher', canComputeNew: false, canResolveRelativePaths: false, consoleParsers: [[parserName: 'Sphinx Documentation Build']], defaultEncoding: '', excludePattern: '', healthy: '', includePattern: '', messagesPattern: '', unHealthy: ''])
    step([$class: 'AnalysisPublisher', canComputeNew: false, defaultEncoding: '', healthy: '', unHealthy: ''])

    if (currentBuild.result == 'FAILURE') {
        slackSend channel: '#lammps-workshop', color: 'bad', message: "(WORKSHOP) Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} failed!"
    } else {
        slackSend channel: '#lammps-workshop', color: 'good', message: "(WORKSHOP) Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} succeeded!"
    }
}
