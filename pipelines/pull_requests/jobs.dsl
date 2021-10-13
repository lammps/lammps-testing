@Grab('org.yaml:snakeyaml:1.17')
import org.yaml.snakeyaml.Yaml

folder('dev/pull_requests')

pipelineJob("dev/pull_requests/checkstyle") {
    properties {
        githubProjectUrl("https://github.com/lammps/lammps/")
        disableConcurrentBuilds()
        pipelineTriggers {
            triggers {
                githubPullRequests {
                    spec("* * * * *")
                    triggerMode('HEAVY_HOOKS')
                    cancelQueued(true)
                    repoProviders {
                        githubPlugin {
                            cacheConnection(true)
                            manageHooks(true)
                            repoPermission('ADMIN')
                        }
                    }
                    events {
                        Open()
                        commitChanged()
                    }
                }
            }
        }
    }

    definition {
        cps {
            script(readFileFromWorkspace('pipelines/pull_requests/checkstyle.groovy'))
            sandbox()
        }
    }
}

pipelineJob("dev/pull_requests/compilation_tests") {
    properties {
        githubProjectUrl("https://github.com/lammps/lammps/")
        disableConcurrentBuilds()
        pipelineTriggers {
            triggers {
                githubPullRequests {
                    spec("* * * * *")
                    triggerMode('HEAVY_HOOKS')
                    cancelQueued(true)
                    repoProviders {
                        githubPlugin {
                            cacheConnection(true)
                            manageHooks(true)
                            repoPermission('ADMIN')
                        }
                    }
                    events {
                        Open()
                        commitChanged()
                    }
                }
            }
        }
    }

    definition {
        cps {
            script(readFileFromWorkspace('pipelines/pull_requests/compilation_tests.groovy'))
            sandbox()
        }
    }
}

pipelineJob("dev/pull_requests/unit_tests") {
    properties {
        githubProjectUrl("https://github.com/lammps/lammps/")
        disableConcurrentBuilds()
        pipelineTriggers {
            triggers {
                githubPullRequests {
                    spec("* * * * *")
                    triggerMode('HEAVY_HOOKS')
                    cancelQueued(true)
                    repoProviders {
                        githubPlugin {
                            cacheConnection(true)
                            manageHooks(true)
                            repoPermission('ADMIN')
                        }
                    }
                    events {
                        Open()
                        commitChanged()
                    }
                }
            }
        }
    }

    definition {
        cps {
            script(readFileFromWorkspace('pipelines/pull_requests/unit_tests.groovy'))
            sandbox()
        }
    }
}

pipelineJob("dev/pull_requests/gpu_unit_tests") {
    properties {
        githubProjectUrl("https://github.com/lammps/lammps/")
        disableConcurrentBuilds()
        pipelineTriggers {
            triggers {
                githubPullRequests {
                    spec("* * * * *")
                    triggerMode('HEAVY_HOOKS')
                    cancelQueued(true)
                    repoProviders {
                        githubPlugin {
                            cacheConnection(true)
                            manageHooks(true)
                            repoPermission('ADMIN')
                        }
                    }
                    events {
                        labelsAdded {
                            label {
                                labels('gpu_unit_tests')
                            }
                        }
                        labelsExist {
                            label {
                                labels('gpu_unit_tests')
                            }
                            skip(false)
                        }
                        labelsAdded {
                            label {
                                labels('ready_for_merge')
                            }
                        }
                        labelsExist {
                            label {
                                labels('ready_for_merge')
                            }
                            skip(false)
                        }
                    }
                }
            }
        }
    }

    definition {
        cps {
            script(readFileFromWorkspace('pipelines/pull_requests/gpu_unit_tests.groovy'))
            sandbox()
        }
    }
}

pipelineJob("dev/pull_requests/ibmxl_ppc64le") {
    properties {
        githubProjectUrl("https://github.com/lammps/lammps/")
        disableConcurrentBuilds()
        pipelineTriggers {
            triggers {
                githubPullRequests {
                    spec("* * * * *")
                    triggerMode('HEAVY_HOOKS')
                    cancelQueued(true)
                    repoProviders {
                        githubPlugin {
                            cacheConnection(true)
                            manageHooks(true)
                            repoPermission('ADMIN')
                        }
                    }
                    events {
                        labelsAdded {
                            label {
                                labels('ppc64le')
                            }
                        }
                        labelsExist {
                            label {
                                labels('ppc64le')
                            }
                            skip(false)
                        }
                        labelsAdded {
                            label {
                                labels('ready_for_merge')
                            }
                        }
                        labelsExist {
                            label {
                                labels('ready_for_merge')
                            }
                            skip(false)
                        }
                    }
                }
            }
        }
    }

    definition {
        cps {
            script(readFileFromWorkspace('pipelines/pull_requests/ibmxl_ppc64le.groovy'))
            sandbox()
        }
    }
}

pipelineJob("dev/pull_requests/run_tests") {
    properties {
        githubProjectUrl("https://github.com/lammps/lammps/")
        disableConcurrentBuilds()
        pipelineTriggers {
            triggers {
                githubPullRequests {
                    spec("* * * * *")
                    triggerMode('HEAVY_HOOKS')
                    cancelQueued(true)
                    repoProviders {
                        githubPlugin {
                            cacheConnection(true)
                            manageHooks(true)
                            repoPermission('ADMIN')
                        }
                    }
                    events {
                        labelsAdded {
                            label {
                                labels('test_runs')
                            }
                        }
                        labelsExist {
                            label {
                                labels('test_runs')
                            }
                            skip(false)
                        }
                        labelsAdded {
                            label {
                                labels('ready_for_merge')
                            }
                        }
                        labelsExist {
                            label {
                                labels('ready_for_merge')
                            }
                            skip(false)
                        }
                    }
                }
            }
        }
    }

    definition {
        cps {
            script(readFileFromWorkspace('pipelines/pull_requests/run_tests.groovy'))
            sandbox()
        }
    }
}

pipelineJob("dev/pull_requests/regression_tests") {
    properties {
        githubProjectUrl("https://github.com/lammps/lammps/")
        disableConcurrentBuilds()
        pipelineTriggers {
            triggers {
                githubPullRequests {
                    spec("* * * * *")
                    triggerMode('HEAVY_HOOKS')
                    cancelQueued(true)
                    repoProviders {
                        githubPlugin {
                            cacheConnection(true)
                            manageHooks(true)
                            repoPermission('ADMIN')
                        }
                    }
                    events {
                        labelsAdded {
                            label {
                                labels('test_for_regression')
                            }
                        }
                        labelsExist {
                            label {
                                labels('test_for_regression')
                            }
                            skip(false)
                        }
                        labelsAdded {
                            label {
                                labels('ready_for_merge')
                            }
                        }
                        labelsExist {
                            label {
                                labels('ready_for_merge')
                            }
                            skip(false)
                        }
                    }
                }
            }
        }
    }

    definition {
        cps {
            script(readFileFromWorkspace('pipelines/pull_requests/regression_tests.groovy'))
            sandbox()
        }
    }
}

pipelineJob("dev/pull_requests/build_docs") {
    properties {
        githubProjectUrl("https://github.com/lammps/lammps/")
        disableConcurrentBuilds()
        pipelineTriggers {
            triggers {
                githubPullRequests {
                    spec("* * * * *")
                    triggerMode('HEAVY_HOOKS')
                    cancelQueued(true)
                    repoProviders {
                        githubPlugin {
                            cacheConnection(true)
                            manageHooks(true)
                            repoPermission('ADMIN')
                        }
                    }
                    events {
                        Open()
                        commitChanged()
                    }
                }
            }
        }
    }

    definition {
        cps {
            script(readFileFromWorkspace('pipelines/pull_requests/build_docs.groovy'))
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

    folder("dev/pull_requests/${container}")

    pipelineJob("dev/pull_requests/${container}/compilation_tests") {
        parameters {
            stringParam('GIT_COMMIT')
            stringParam('WORKSPACE_PARENT')
            stringParam('CONTAINER_NAME', container)
            stringParam('CCACHE_DIR', '.ccache')
        }

        definition {
            cps {
                script(readFileFromWorkspace('pipelines/develop/container_compilation_tests.groovy'))
                sandbox()
            }
        }
    }

    config.builds.each { name ->
        pipelineJob("dev/pull_requests/${container}/${name}") {
            parameters {
                stringParam('GIT_COMMIT')
                stringParam('WORKSPACE_PARENT')
                stringParam('CCACHE_DIR', '.ccache')
                stringParam('CONTAINER_NAME', container)
                stringParam('CONTAINER_IMAGE', config.container_image)
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
        folder("dev/pull_requests/${container}/run_tests")

        config.run_tests.each { name ->
            pipelineJob("dev/pull_requests/${container}/run_tests/${name}") {
                parameters {
                    stringParam('GIT_COMMIT')
                    stringParam('WORKSPACE_PARENT')
                    stringParam('CCACHE_DIR')
                    stringParam('CONTAINER_NAME', container)
                    stringParam('CONTAINER_IMAGE', config.container_image)
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
        folder("dev/pull_requests/${container}/regression_tests")

        config.regression_tests.each { name ->
            pipelineJob("dev/pull_requests/${container}/regression_tests/${name}") {
                parameters {
                    stringParam('GIT_COMMIT')
                    stringParam('WORKSPACE_PARENT')
                    stringParam('CCACHE_DIR')
                    stringParam('CONTAINER_NAME', container)
                    stringParam('CONTAINER_IMAGE', config.container_image)
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
        folder("dev/pull_requests/${container}/unit_tests")

        config.unit_tests.each { name ->
            pipelineJob("dev/pull_requests/${container}/unit_tests/${name}") {
                parameters {
                    stringParam('GIT_COMMIT')
                    stringParam('GITHUB_PR_NUMBER')
                    stringParam('WORKSPACE_PARENT')
                    stringParam('CCACHE_DIR')
                    stringParam('CONTAINER_NAME', container)
                    stringParam('CONTAINER_IMAGE', config.container_image)
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
