folder('tutorial/master')

def scripts = ['serial', 'shlib', 'openmpi', 'build-docs']

scripts.each { name ->
    pipelineJob("tutorial/master/${name}") {
        triggers {
            githubPush()
        }

        concurrentBuild(false)

        definition {
            cps {
                script(readFileFromWorkspace('pipelines/tutorial-master/master.groovy'))
                sandbox()
            }
        }
    }
}

folder('tutorial/master/cmake')

def cmake_scripts = ['cmake-serial']

cmake_scripts.each { name ->
    pipelineJob("tutorial/master/cmake/${name}") {
        triggers {
            githubPush()
        }

        concurrentBuild(false)

        definition {
            cps {
                script(readFileFromWorkspace('pipelines/tutorial-master/master.groovy'))
                sandbox()
            }
        }
    }
}
