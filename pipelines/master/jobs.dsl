folder('lammps/master')

def scripts = ['regression']

scripts.each { name ->
    pipelineJob("lammps/master/${name}") {
        triggers {
            githubPush()
        }

        concurrentBuild(false)

        definition {
            cps {
                script(readFileFromWorkspace('pipelines/master/master.groovy'))
                sandbox()
            }
        }
    }
}

pipelineJob("lammps/master/cmake/coverity-scan") {
    triggers {
        cron('@weekly')
    }

    concurrentBuild(false)
    disabled()

    definition {
        cps {
            script(readFileFromWorkspace('pipelines/master/master.groovy'))
            sandbox()
        }
    }
}
