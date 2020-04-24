@Grab('org.yaml:snakeyaml:1.17')
import org.yaml.snakeyaml.Yaml

folder('dev/master')

pipelineJob("dev/master/compilation_tests") {
    properties {
        pipelineTriggers {
            triggers {
                githubPush()
            }
        }
    }

    definition {
        cps {
            script(readFileFromWorkspace('pipelines/new_master/compilation_tests.groovy'))
        }
    }
}

pipelineJob("dev/master/build-docs") {
    properties {
        pipelineTriggers {
            triggers {
                githubPush()
            }
        }
    }

    definition {
        cps {
            script(readFileFromWorkspace('pipelines/new_master/build-docs.groovy'))
        }
    }
}

def workspace = SEED_JOB.getWorkspace()
def scripts = workspace.child('scripts/simple')
def configurations = scripts.list('*.yml')

configurations.each { yaml_file ->
    def config = new Yaml().load(yaml_file.readToString())
    def container = yaml_file.getBaseName()

    folder("dev/master/${container}")

    config.builds.each { name ->
        pipelineJob("dev/master/${container}/${name}") {
            parameters {
                stringParam('GIT_COMMIT')
                stringParam('WORKSPACE_PARENT')
                stringParam('CONTAINER_NAME', container)
                stringParam('CONTAINER_IMAGE', config.container_image)
            }

            definition {
                cps {
                    script(readFileFromWorkspace('pipelines/new_master/build.groovy'))
                }
            }
        }
    }
}
