folder('lammps/pull-requests')

def scripts = ['build-docs-pr']

scripts.each { name ->
    pipelineJob("lammps/pull-requests/${name}") {
        properties {
            githubProjectUrl("https://github.com/lammps/lammps/")
        }

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

        concurrentBuild(false)

        definition {
            cps {
                script(readFileFromWorkspace('pipelines/pull-requests/pr.groovy'))
                sandbox()
            }
        }
    }
}

pipelineJob("lammps/pull-requests/regression-pr") {
    properties {
        githubProjectUrl("https://github.com/lammps/lammps/")
    }

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
                labelsAdded {
                    label {
                        labels('full-regression-test')
                    }
                }
                labelsExist {
                    label {
                        labels('full-regression-test')
                    }
		    skip(false)
                }
            }
        }
    }

    concurrentBuild(false)

    definition {
        cps {
            script(readFileFromWorkspace('pipelines/pull-requests/pr.groovy'))
            sandbox()
        }
    }
}

