folder('website')

pipelineJob("website/build_www_lammps_org") {
    logRotator {
       numToKeep(100)
    }

    properties {
        disableConcurrentBuilds()
        pipelineTriggers {
            triggers {
                githubPush()
            }
        }
    }

    definition {
        cps {
            script(readFileFromWorkspace('pipelines/website/build_www_lammps_org.groovy'))
            sandbox()
        }
    }
}
