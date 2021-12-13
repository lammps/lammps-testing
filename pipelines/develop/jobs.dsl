@Grab('org.yaml:snakeyaml:1.17')
import org.yaml.snakeyaml.Yaml

folder('dev/develop')
folder('dev/release')

pipelineJob("dev/develop/checkstyle") {
    quietPeriod(120)

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
            script(readFileFromWorkspace('pipelines/develop/checkstyle.groovy'))
            sandbox()
        }
    }
}

pipelineJob("dev/develop/compilation_tests") {
    quietPeriod(120)

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
            script(readFileFromWorkspace('pipelines/develop/compilation_tests.groovy'))
            sandbox()
        }
    }
}

pipelineJob("dev/develop/run_tests") {
    quietPeriod(120)

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
            script(readFileFromWorkspace('pipelines/develop/run_tests.groovy'))
            sandbox()
        }
    }
}

pipelineJob("dev/develop/regression_tests") {
    quietPeriod(120)

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
            script(readFileFromWorkspace('pipelines/develop/regression_tests.groovy'))
            sandbox()
        }
    }
}

pipelineJob("dev/develop/build_docs") {
    quietPeriod(120)

    logRotator {
       numToKeep(100)
    }

    properties {
        pipelineTriggers {
            triggers {
                githubPush()
            }
        }
    }

    definition {
        cps {
            script(readFileFromWorkspace('pipelines/develop/build_docs.groovy'))
            sandbox()
        }
    }
}

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


pipelineJob("dev/develop/unit_tests") {
    quietPeriod(120)

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
            script(readFileFromWorkspace('pipelines/develop/unit_tests.groovy'))
            sandbox()
        }
    }
}

folder('dev/develop/docker')


pipelineJob("dev/develop/docker_containers") {
    quietPeriod(120)

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
            script(readFileFromWorkspace('pipelines/develop/docker_containers.groovy'))
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

    folder("dev/develop/${container}")

    pipelineJob("dev/develop/${container}/compilation_tests") {
        parameters {
            stringParam('GIT_COMMIT')
            stringParam('WORKSPACE_PARENT')
            stringParam('CONTAINER_NAME', container)
        }

        logRotator {
           numToKeep(100)
        }

        definition {
            cps {
                script(readFileFromWorkspace('pipelines/develop/container_compilation_tests.groovy'))
                sandbox()
            }
        }
    }

    config.builds.each { name ->
        pipelineJob("dev/develop/${container}/${name}") {
            parameters {
                stringParam('GIT_COMMIT')
                stringParam('WORKSPACE_PARENT')
                stringParam('CCACHE_DIR', '.ccache')
                stringParam('CONTAINER_NAME', container)
                stringParam('CONTAINER_IMAGE', config.container_image)
            }

            logRotator {
               numToKeep(100)
            }

            definition {
                cps {
                    script(readFileFromWorkspace('pipelines/develop/build.groovy'))
                    sandbox()
                }
            }
        }
    }

    if(config.containsKey('run_tests')){
        folder("dev/develop/${container}/run_tests")

        config.run_tests.each { name ->
            pipelineJob("dev/develop/${container}/run_tests/${name}") {
                parameters {
                    stringParam('GIT_COMMIT')
                    stringParam('WORKSPACE_PARENT')
                    stringParam('CCACHE_DIR', '.ccache')
                    stringParam('CONTAINER_NAME', container)
                    stringParam('CONTAINER_IMAGE', config.container_image)
                }

                logRotator {
                   numToKeep(100)
                }

                definition {
                    cps {
                        script(readFileFromWorkspace('pipelines/develop/run.groovy'))
                        sandbox()
                    }
                }
            }
        }
    }

    if(config.containsKey('regression_tests')){
        folder("dev/develop/${container}/regression_tests")

        config.regression_tests.each { name ->
            pipelineJob("dev/develop/${container}/regression_tests/${name}") {
                parameters {
                    stringParam('GIT_COMMIT')
                    stringParam('WORKSPACE_PARENT')
                    stringParam('CCACHE_DIR', '.ccache')
                    stringParam('CONTAINER_NAME', container)
                    stringParam('CONTAINER_IMAGE', config.container_image)
                }

                logRotator {
                   numToKeep(100)
                }

                definition {
                    cps {
                        script(readFileFromWorkspace('pipelines/develop/regression.groovy'))
                        sandbox()
                    }
                }
            }
        }
    }

    if(config.containsKey('unit_tests')){
        folder("dev/develop/${container}/unit_tests")

        config.unit_tests.each { name ->
            pipelineJob("dev/develop/${container}/unit_tests/${name}") {
                parameters {
                    stringParam('GIT_COMMIT')
                    stringParam('WORKSPACE_PARENT')
                    stringParam('CCACHE_DIR', '.ccache')
                    stringParam('CONTAINER_NAME', container)
                    stringParam('CONTAINER_IMAGE', config.container_image)
                }

                logRotator {
                   numToKeep(100)
                }

                definition {
                    cps {
                        script(readFileFromWorkspace('pipelines/develop/run_unit_tests.groovy'))
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
        properties {
          disableConcurrentBuilds()
        }

        logRotator {
           numToKeep(100)
        }

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
                scriptPath("pipelines/develop/singularity_container.groovy")
            }
        }
    }
}

def docker_config_file = workspace.child('containers/docker.yml')
def docker_config = new Yaml().load(docker_config_file.readToString())
folder("dev/develop/docker")

docker_config.containers.each { name ->
    pipelineJob("dev/develop/docker/${name}") {
        parameters {
            stringParam('GIT_COMMIT')
            stringParam('WORKSPACE_PARENT')
        }

        logRotator {
           numToKeep(100)
        }

        definition {
            cps {
                script(readFileFromWorkspace('pipelines/develop/docker_container.groovy'))
                sandbox()
            }
        }
    }
}

folder('dev/develop/static_analysis')

pipelineJob("dev/develop/static_analysis/cmake_coverity") {
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

    logRotator {
       numToKeep(100)
    }

    definition {
        cps {
            script(readFileFromWorkspace('pipelines/develop/cmake_coverity.groovy'))
            sandbox()
        }
    }
}

folder('dev/develop/macos_arm64/unit_tests')

pipelineJob("dev/develop/macos_arm64/unit_tests/cmake_mpi_openmp_smallbig_clang_shared") {
    quietPeriod(120)

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
            script(readFileFromWorkspace('pipelines/develop/macos_unittest.groovy'))
            sandbox()
        }
    }
}
