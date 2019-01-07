folder('lammps/pull-requests')

def scripts = ['new-serial-pr', 'new-shlib-pr', 'new-openmpi-pr', 'new-build-docs-pr']

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

folder('lammps/pull-requests/cmake')

def cmake_scripts = ['new-cmake-serial-pr']

cmake_scripts.each { name ->
    pipelineJob("lammps/pull-requests/cmake/${name}") {
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
