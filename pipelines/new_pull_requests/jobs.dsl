@Grab('org.yaml:snakeyaml:1.17')
import org.yaml.snakeyaml.Yaml

folder('dev/pull_requests')

pipelineJob("dev/pull_requests/compilation_tests") {
    properties {
        githubProjectUrl("https://github.com/lammps/lammps/")
        disableConcurrentBuilds()
        pipelineTriggers {
            triggers {
                githubPullRequests {
                    spec("* * * * *")
                    triggerMode('HEAVY_HOOKS')
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
            script(readFileFromWorkspace('pipelines/new_pull_requests/compilation_tests.groovy'))
        }
    }
}

//pipelineJob("dev/pull_requests/build-docs") {
//    properties {
//        pipelineTriggers {
//            triggers {
//                githubPush()
//            }
//        }
//    }
//
//    definition {
//        cps {
//            script(readFileFromWorkspace('pipelines/new_master/build-docs.groovy'))
//        }
//    }
//}

def workspace = SEED_JOB.getWorkspace()
def scripts = workspace.child('scripts/simple')
def configurations = scripts.list('*.yml')

configurations.each { yaml_file ->
    def config = new Yaml().load(yaml_file.readToString())
    def container = yaml_file.getBaseName()

    folder("dev/pull_requests/${container}")

    config.builds.each { name ->
        pipelineJob("dev/pull_requests/${container}/${name}") {
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
