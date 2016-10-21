folder('dsl')

pipelineJob('dsl/serial-gcc') {
    definition {
        cpsScm {
            scm {
                github('lammps/lammps-testing', 'pipelines')
            }
            scriptPath('pipelines/unstable/serial-gcc.groovy')
        }
    }
}
