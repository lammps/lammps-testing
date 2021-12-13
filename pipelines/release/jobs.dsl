folder('dev/release')

pipelineJob("dev/release/build_docs") {
    quietPeriod(120)

    properties {
        pipelineTriggers {
            triggers {
                githubPush()
            }
        }
    }

    definition {
        cps {
            script(readFileFromWorkspace('pipelines/release/build_docs.groovy'))
            sandbox()
        }
    }
}
