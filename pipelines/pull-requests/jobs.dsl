folder('lammps/pull-requests')

def scripts = ['serial-pr', 'shlib-pr', 'openmpi-pr', 'build-docs-pr', 'kokkos-omp-pr']

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

pipelineJob("lammps/pull-requests/testing-pr") {
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
                        labels('test-for-regression')
                    }
                }
                labelsExist {
                    label {
                        labels('test-for-regression')
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

pipelineJob("lammps/pull-requests/testing-omp-pr") {
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
                        labels('test-for-regression')
                    }
                }
                labelsExist {
                    label {
                        labels('test-for-regression')
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

folder('lammps/pull-requests/cmake')

def cmake_scripts = ['cmake-serial-pr']

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

pipelineJob("lammps/pull-requests/cmake/cmake-win32-serial") {
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
                        labels('cross_compilation')
                    }
                }
                labelsExist {
                    label {
                        labels('cross_compilation')
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

pipelineJob("lammps/pull-requests/cmake/cmake-win64-serial") {
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
                        labels('cross_compilation')
                    }
                }
                labelsExist {
                    label {
                        labels('cross_compilation')
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
