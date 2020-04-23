@Grab('org.yaml:snakeyaml:1.17')
import org.yaml.snakeyaml.Yaml

folder('dev/master')

pipelineJob("dev/master/compilation_tests") {
    triggers {
        githubPush()
    }

    definition {
        cpsScm {
            scm {
                git {
                    branch('lammps_test')
                    remote {
                        github('lammps/lammps-testing')
                        credentials('lammps-jenkins')
                    }
                    extensions {
                        ignoreNotifyCommit()
                    }
                }
            }
            scriptPath('pipelines/new_master/compilation_tests.groovy')
        }
    }
}

def workspace = SEED_JOB.getWorkspace()
def scripts = workspace.child('scripts/simple')
def configurations = scripts.list('*.yml')

configurations.each { yaml_file ->
    def config = new Yaml().load(yaml_file.readToString())
    def container = yaml_file.getBaseName()

    pipelineJob("dev/master/${container}_compilation_tests") {
        parameters {
            stringParam('GIT_COMMIT')
            stringParam('WORKSPACE_PARENT')
            stringParam('CONTAINER_NAME', container)
            stringParam('CONTAINER_DISPLAY_NAME', config.display_name)
            stringParam('CONTAINER_BUILDS', config.builds.join(','))
        }

        definition {
            cpsScm {
                scm {
                    git {
                        branch('lammps_test')
                        remote {
                            github('lammps/lammps-testing')
                            credentials('lammps-jenkins')
                        }
                    }
                }
                scriptPath("pipelines/new_master/container.groovy")
            }
        }
    }

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
                cpsScm {
                    scm {
                        git {
                            branch('lammps_test')
                            remote {
                                github('lammps/lammps-testing')
                                credentials('lammps-jenkins')
                            }
                        }
                    }
                    scriptPath("pipelines/new_master/build.groovy")
                }
            }
        }
    }
}
