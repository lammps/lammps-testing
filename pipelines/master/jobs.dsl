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
            script(readFileFromWorkspace('pipelines/master/checkstyle.groovy'))
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
            script(readFileFromWorkspace('pipelines/master/compilation_tests.groovy'))
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
            script(readFileFromWorkspace('pipelines/master/run_tests.groovy'))
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
            script(readFileFromWorkspace('pipelines/master/regression_tests.groovy'))
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
            script(readFileFromWorkspace('pipelines/master/build_docs.groovy'))
            sandbox()
        }
    }
}


pipelineJob("dev/master/unit_tests") {
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
            script(readFileFromWorkspace('pipelines/master/unit_tests.groovy'))
            sandbox()
        }
    }
}

folder('dev/master/docker')


pipelineJob("dev/master/docker_containers") {
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
            script(readFileFromWorkspace('pipelines/master/docker_containers.groovy'))
            sandbox()
        }
    }
}

def workspace = SEED_JOB.getWorkspace()
def scripts = workspace.child('scripts')
def configurations = scripts.list('*.yml')

configurations.each { yaml_file ->
    def config = new Yaml().load(yaml_file.readToString())
    def container = yaml_file.getBaseName()

    folder("dev/master/${container}")

    pipelineJob("dev/master/${container}/compilation_tests") {
        parameters {
            stringParam('GIT_COMMIT')
            stringParam('WORKSPACE_PARENT')
            stringParam('CONTAINER_NAME', container)
        }

        definition {
            cps {
                script(readFileFromWorkspace('pipelines/master/container_compilation_tests.groovy'))
                sandbox()
            }
        }
    }

    config.builds.each { name ->
        pipelineJob("dev/master/${container}/${name}") {
            parameters {
                stringParam('GIT_COMMIT')
                stringParam('WORKSPACE_PARENT')
                stringParam('CCACHE_DIR', '.ccache')
                stringParam('CONTAINER_NAME', container)
                stringParam('CONTAINER_IMAGE', config.container_image)
            }

            definition {
                cps {
                    script(readFileFromWorkspace('pipelines/master/build.groovy'))
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
                    stringParam('CCACHE_DIR', '.ccache')
                    stringParam('CONTAINER_NAME', container)
                    stringParam('CONTAINER_IMAGE', config.container_image)
                }

                definition {
                    cps {
                        script(readFileFromWorkspace('pipelines/master/run.groovy'))
                        sandbox()
                    }
                }
            }
        }
    }

    if(config.containsKey('regression_tests')){
        folder("dev/master/${container}/regression_tests")

        config.regression_tests.each { name ->
            pipelineJob("dev/master/${container}/regression_tests/${name}") {
                parameters {
                    stringParam('GIT_COMMIT')
                    stringParam('WORKSPACE_PARENT')
                    stringParam('CCACHE_DIR', '.ccache')
                    stringParam('CONTAINER_NAME', container)
                    stringParam('CONTAINER_IMAGE', config.container_image)
                }

                definition {
                    cps {
                        script(readFileFromWorkspace('pipelines/master/regression.groovy'))
                        sandbox()
                    }
                }
            }
        }
    }

    if(config.containsKey('unit_tests')){
        folder("dev/master/${container}/unit_tests")

        config.unit_tests.each { name ->
            pipelineJob("dev/master/${container}/unit_tests/${name}") {
                parameters {
                    stringParam('GIT_COMMIT')
                    stringParam('WORKSPACE_PARENT')
                    stringParam('CCACHE_DIR', '.ccache')
                    stringParam('CONTAINER_NAME', container)
                    stringParam('CONTAINER_IMAGE', config.container_image)
                }

                definition {
                    cps {
                        script(readFileFromWorkspace('pipelines/master/run_unit_tests.groovy'))
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

                        branches('master')
                    }
                }
                scriptPath("pipelines/master/singularity_container.groovy")
            }
        }
    }
}

def docker_config_file = workspace.child('containers/docker.yml')
def docker_config = new Yaml().load(docker_config_file.readToString())
folder("dev/master/docker")

docker_config.containers.each { name ->
    pipelineJob("dev/master/docker/${name}") {
        parameters {
            stringParam('GIT_COMMIT')
            stringParam('WORKSPACE_PARENT')
        }

        definition {
            cps {
                script(readFileFromWorkspace('pipelines/master/docker_container.groovy'))
                sandbox()
            }
        }
    }
}

folder('dev/master/static_analysis')

pipelineJob("dev/master/static_analysis/cmake_coverity") {
    properties {
        disableConcurrentBuilds()
        pipelineTriggers {
            triggers {
                cron {
                    spec("H 2 * * 5")
                }
            }
        }
    }

    definition {
        cps {
            script(readFileFromWorkspace('pipelines/master/cmake_coverity.groovy'))
            sandbox()
        }
    }
}
