folder('tutorial/pull-requests')

def scripts = ['serial-pr', 'shlib-pr', 'openmpi-pr', 'build-docs-pr']

scripts.each { name ->
    pipelineJob("tutorial/pull-requests/${name}") {
        properties {
            githubProjectUrl("https://github.com/lammps/lammps-git-tutorial/")
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
                script(readFileFromWorkspace('pipelines/tutorial-pull-requests/pr.groovy'))
                sandbox()
            }
        }
    }
}


folder('tutorial/pull-requests/cmake')

def cmake_scripts = ['cmake-serial-pr']

cmake_scripts.each { name ->
    pipelineJob("tutorial/pull-requests/cmake/${name}") {
        properties {
            githubProjectUrl("https://github.com/lammps/lammps-git-tutorial/")
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
                script(readFileFromWorkspace('pipelines/tutorial-pull-requests/pr.groovy'))
                sandbox()
            }
        }
    }
}
