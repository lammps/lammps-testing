folder('dsl')

pipelineJob('dsl/serial-gcc') {
    definition {
        cpsScm {
            scm {
                github('lammps/lammps-testing', 'pipelines') {
                    credentialsId('lammps-jenkins')
                }
            }
            scriptPath('pipelines/unstable/serial-gcc.groovy')
        }
    }
}
