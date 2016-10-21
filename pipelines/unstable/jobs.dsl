folder('dsl')

pipelineJob('dsl/serial-gcc') {
    definition {
        cps {
            script(readFileFromWorkspace('pipelines/unstable/serial-gcc.groovy'))
            sandbox()
        }
    }
}
