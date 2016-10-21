folder('dsl')

pipelineJob('dsl/serial-gcc') {
    triggers {
        githubPush()
    }

    definition {
        cpsScm {
            scm {
                git {
                    remote {
                        github('lammps/lammps-testing')
                        credentials('lammps-jenkins')
                    }
                    branches('pipelines')
                }
            }
            scriptPath('pipelines/unstable/serial-gcc.groovy')
        }
    }
}
