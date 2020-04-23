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
                }
            }
            scriptPath('pipelines/new_master/compilation_tests.groovy')
        }
    }
}

def workspace = hudson.model.Executor.currentExecutor().getCurrentWorkspace()
def scripts = workspace.child('scripts/simple')

def containers = ['ubuntu', 'centos7', 'windows']

containers.each { container ->
    pipelineJob("dev/master/${container}_compilation_tests") {
        parameters {
            stringParam('GIT_COMMIT')
            stringParam('WORKSPACE_PARENT')
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
                scriptPath("pipelines/new_master/${container}.groovy")
            }
        }
    }

    folder("dev/master/${container}")

    def container_scripts = scripts.child(container).list()

    container_scripts.each { script_name ->
	def name = script_name.getBaseName()
        pipelineJob("dev/master/${container}/${name}") {
            parameters {
                stringParam('GIT_COMMIT')
                stringParam('WORKSPACE_PARENT')
                stringParam('CONTAINER_NAME', "${container}")
                stringParam('CONTAINER_IMAGE', 'lammps_testing:ubuntu_latest')
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
