@Grab('org.yaml:snakeyaml:1.17')
import org.yaml.snakeyaml.Yaml

folder('dev/master')

pipelineJob("dev/master/checkstyle") {
    quietPeriod(120)

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
            script(readFileFromWorkspace('pipelines/new_master/checkstyle.groovy'))
            sandbox()
        }
    }
}

pipelineJob("dev/master/compilation_tests") {
    quietPeriod(120)

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
            script(readFileFromWorkspace('pipelines/new_master/compilation_tests.groovy'))
            sandbox()
        }
    }
}

pipelineJob("dev/master/run_tests") {
    quietPeriod(120)

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
            script(readFileFromWorkspace('pipelines/new_master/run_tests.groovy'))
            sandbox()
        }
    }
}

pipelineJob("dev/master/regression_tests") {
    quietPeriod(120)

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
            script(readFileFromWorkspace('pipelines/new_master/regression_tests.groovy'))
            sandbox()
        }
    }
}

pipelineJob("dev/master/build_docs") {
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
            script(readFileFromWorkspace('pipelines/new_master/build_docs.groovy'))
            sandbox()
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
                    sandbox()
                }
            }
        }
    }

    if(config.containsKey('run_tests')){
        folder("dev/master/${container}/run_tests")

        config.run_tests.each { name ->
            pipelineJob("dev/master/${container}/run_tests/${name}") {
                parameters {
                    stringParam('GIT_COMMIT')
                    stringParam('WORKSPACE_PARENT')
                    stringParam('CONTAINER_NAME', container)
                    stringParam('CONTAINER_IMAGE', config.container_image)
                }

                definition {
                    cps {
                        script(readFileFromWorkspace('pipelines/new_master/run.groovy'))
                        sandbox()
                    }
                }
            }
        }
    }

    if(config.containsKey('run_tests')){
        folder("dev/master/${container}/regression_tests")

        config.run_tests.each { name ->
            pipelineJob("dev/master/${container}/regression_tests/${name}") {
                parameters {
                    stringParam('GIT_COMMIT')
                    stringParam('WORKSPACE_PARENT')
                    stringParam('CONTAINER_NAME', container)
                    stringParam('CONTAINER_IMAGE', config.container_image)
                }

                definition {
                    cps {
                        script(readFileFromWorkspace('pipelines/new_master/regression.groovy'))
                        sandbox()
                    }
                }
            }
        }
    }
}

folder('dev/containers')

def container_folder = workspace.child('containers/singularity')
def container_definitions = container_folder.list('*.def')

container_definitions.each { definition_file ->
    def name = definition_file.getBaseName()

    pipelineJob("dev/containers/${name}") {
        concurrentBuild(false)

        definition {
            cpsScm {
                scm {
                    git {
                        remote {
                            github('lammps/lammps-testing')
                            credentials('lammps-jenkins')
                        }

                        branches('lammps_test')
                    }
                }
                scriptPath("pipelines/new_master/singularity_container.groovy")
            }
        }
    }
}
