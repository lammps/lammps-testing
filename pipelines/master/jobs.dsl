folder('lammps/master')

def scripts = ['serial', 'shlib', 'openmpi', 'testing', 'build-docs', 'kokkos_omp', 'regression', 'testing-omp', 'cmake-testing-omp', 'serial-clang', 'shlib-clang', 'openmpi-clang']

scripts.each { name ->
    pipelineJob("lammps/master/${name}") {
        triggers {
            githubPush()
        }

        concurrentBuild(false)
        quietPeriod(600)

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
                              includedRegions("pipelines/master/${name}.groovy")
                          }
                        }
                    }
                }
                scriptPath("pipelines/master/${name}.groovy")
            }
        }
    }
}
