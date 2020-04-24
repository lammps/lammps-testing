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

    def get_configuration = { yaml_file ->
        def name = yaml_file.name.take(yaml_file.name.lastIndexOf('.'))
        return ["${name}": readYaml(file: yaml_file.path)]
    }

    def configurations = yaml_files.collectEntries { yaml_file -> get_configuration(yaml_file)  }

    configurations.each { container, config ->
        stage("${container}") {
            echo "Running ${config.display_name}"

            def jobs = [:]

            for (build in config.builds) {
                jobs["${build}"] = {
                    build job: "${container}/${build}",
                        parameters: [
                            string(name: 'GIT_COMMIT', value: commit.GIT_COMMIT),
                            string(name: 'WORKSPACE_PARENT', value: env.WORKSPACE),
                            ]
                }
            }

            parallel jobs
        }
    }
}
