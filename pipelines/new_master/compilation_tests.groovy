node('atlas2') {
    stage('Checkout') {
        dir('lammps') {
            commit = checkout([$class: 'GitSCM', branches: [[name: '*/master']], doGenerateSubmoduleConfigurations: false, extensions: [[$class: 'CloneOption', depth: 1, noTags: false, reference: '', shallow: true]], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'lammps-jenkins', url: 'https://github.com/lammps/lammps']]])
            env.GIT_COMMIT = commit
        }
        
        dir('lammps-testing') {
            checkout changelog: false, poll: false, scm: [$class: 'GitSCM', branches: [[name: '*/lammps_test']], doGenerateSubmoduleConfigurations: false, extensions: [], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'lammps-jenkins', url: 'https://github.com/lammps/lammps-testing']]]
        }
    }
    
    stage('Build') {
        parallel(
            "ubuntu": {
                build job: 'ubuntu', parameters: [string(name: 'GIT_COMMIT', value: commit.GIT_COMMIT), string(name: 'WORKSPACE_PARENT', value: env.WORKSPACE)]
            },
            "centos7": {
                build job: 'centos7', parameters: [string(name: 'GIT_COMMIT', value: commit.GIT_COMMIT), string(name: 'WORKSPACE_PARENT', value: env.WORKSPACE)]
            },
            "windows": {
                build job: 'windows', parameters: [string(name: 'GIT_COMMIT', value: commit.GIT_COMMIT), string(name: 'WORKSPACE_PARENT', value: env.WORKSPACE)]
            }
        )
    }
}
