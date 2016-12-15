folder('lammps/master-dsl')

def scripts = ['serial', 'shlib', 'openmpi', 'testing']

scripts.each { name ->
    pipelineJob("lammps/master-dsl/${name}") {
        triggers {
            githubPush()
        }

        concurrentBuild(false)
        quietPeriod(10)

        definition {
            cpsScm {
                scm {
                    git {
                        remote {
                            github('lammps/lammps-testing')
                            credentials('lammps-jenkins')
                        }

                        branches('pipelines')

                        configure { gitScm ->
                            gitScm / 'extensions' << 'hudson.plugins.git.extensions.impl.PathRestriction' {
                              includedRegions("pipelines/master/${name}.groovy")
                              excludedRegions('')
                          }
                        }
                    }
                }
                scriptPath("pipelines/master/${name}.groovy")
            }
        }
    }
}
