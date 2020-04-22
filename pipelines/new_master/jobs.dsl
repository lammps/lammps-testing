folder('lammps/dev/master')

pipelineJob("lammps/dev/master/compilation_tests") {
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

pipelineJob("lammps/dev/master/ubuntu") {
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
            scriptPath('pipelines/new_master/ubuntu.groovy')
        }
    }
}

pipelineJob("lammps/dev/master/centos7") {
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
            scriptPath('pipelines/new_master/centos7.groovy')
        }
    }
}

pipelineJob("lammps/dev/master/windows") {
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
            scriptPath('pipelines/new_master/windows.groovy')
        }
    }
}
