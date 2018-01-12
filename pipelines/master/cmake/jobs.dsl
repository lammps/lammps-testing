folder('lammps/master/cmake')

def scripts = ['serial', 'openmpi', 'enable_all']

def packages = ['ASPHERE']

scripts.each { name ->
    pipelineJob("lammps/master/cmake/${name}") {
        triggers {
            githubPush()
        }

        concurrentBuild(false)
        quietPeriod(300)

        definition {
            cpsScm {
                scm {
                    git {
                        remote {
                            github('lammps/lammps-testing')
                            credentials('lammps-jenkins')
                        }

                        branches('master')

                        configure { gitScm ->
                            gitScm / 'extensions' << 'hudson.plugins.git.extensions.impl.PathRestriction' {
                              includedRegions("pipelines/master/cmake/${name}.groovy")
                          }
                        }
                    }
                }
                scriptPath("pipelines/master/cmake/${name}.groovy")
            }
        }
    }
}

folder('lammps/master/cmake/packages')

packages.each { name ->
    pipelineJob("lammps/master/cmake/packages/${name}") {
        triggers {
            githubPush()
        }

        environmentVariables {
            env("PACKAGE", name)
        }

        concurrentBuild(false)
        quietPeriod(300)

        definition {
            cpsScm {
                scm {
                    git {
                        remote {
                            github('lammps/lammps-testing')
                            credentials('lammps-jenkins')
                        }

                        branches('master')

                        configure { gitScm ->
                            gitScm / 'extensions' << 'hudson.plugins.git.extensions.impl.PathRestriction' {
                              includedRegions("pipelines/master/cmake/build_package.groovy")
                          }
                        }
                    }
                }
                scriptPath("pipelines/master/cmake/build_package.groovy")
            }
        }
    }
}
