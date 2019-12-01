def project_url = 'https://github.com/lammps/lammps.git'
def shallow_clone = true
node('atlas2'){
    stage('Checkout') {
        dir('lammps') {
            branch_name = "origin-pull/pull/${env.GITHUB_PR_NUMBER}/head"
            refspec = "+refs/pull/${env.GITHUB_PR_NUMBER}/head:refs/remotes/origin-pull/pull/${env.GITHUB_PR_NUMBER}/head"
            checkout([$class: 'GitSCM', branches: [[name: branch_name]], doGenerateSubmoduleConfigurations: false, extensions: [[$class: 'CleanCheckout']], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'lammps-jenkins', name: 'origin-pull', refspec: refspec, url: project_url]]])
        }
    }
    
    gitHubPRStatus githubPRMessage('head run started')
    
    stage('Whitespace') {
        sh 'egrep -Rn "\\s+$"  lammps/src/ > whitespace.log || true'
        recordIssues  qualityGates: [[threshold: 1, type: 'TOTAL', unstable: false]], filters: [includeFile('.*\\.cpp'), includeFile('.*\\.h'), excludeFile('lammps/src/USER-MGPT/*')], tools: [groovyScript(parserId: 'whitespace', pattern: 'whitespace.log')]
    }
    
    githubPRStatusPublisher statusMsg: githubPRMessage('head run ended'), unstableAs: 'SUCCESS'

    if (currentBuild.result == 'FAILURE') {
        slackSend color: 'bad', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} failed!"
    } else {
        slackSend color: 'good', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} succeeded!"
    }
}
