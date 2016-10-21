pipelineJob('serial-gcc') {
    definition {
        cps {
            script(readFileFromWorkspace('pipelines/unstable/serial-gcc.groovy'))
            sandbox()
        }
    }
}
