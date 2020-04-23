node('atlas2') {
    stage('Checkout') {
        dir('lammps') {
            commit = checkout([$class: 'GitSCM', branches: [[name: '*/master']], doGenerateSubmoduleConfigurations: false, extensions: [[$class: 'CloneOption', depth: 1, noTags: false, reference: '', shallow: true]], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'lammps-jenkins', url: 'https://github.com/lammps/lammps']]])
        }
        
        dir('lammps-testing') {
            checkout changelog: false, poll: false, scm: [$class: 'GitSCM', branches: [[name: '*/lammps_test']], doGenerateSubmoduleConfigurations: false, extensions: [], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'lammps-jenkins', url: 'https://github.com/lammps/lammps-testing']]]
        }
    }

    def yaml_files = findFiles glob: 'lammps-testing/scripts/simple/*.yml'
    def configurations = yaml_files.collect { yaml_file -> yaml_file.name.take(yaml_file.name.lastIndexOf('.'))  }

    def jobs = configurations.collectEntries { container ->
        ["${container}": {
            build job: "${container}_compilation_tests", parameters: [string(name: 'GIT_COMMIT', value: commit.GIT_COMMIT), string(name: 'WORKSPACE_PARENT', value: env.WORKSPACE)]
        }]
    }
    
    stage('Build') {
        parallel jobs
    }
}
