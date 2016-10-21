folder('dsl')

pipelineJob('dsl/serial-gcc') {
    definition {
        cpsScm {
            github('lammps/lammps-testing', 'pipelines')
            scriptPath('pipelines/unstable/serial-gcc.groovy')
        }
    }
}
