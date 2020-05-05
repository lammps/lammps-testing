folder('lammps/pull-requests')

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

