folder('lammps-git-training/master')

def scripts = ['serial', 'shlib', 'openmpi', 'testing', 'build-docs']

scripts.each { name ->
    pipelineJob("lammps-git-training/master/${name}") {
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

                        branches('lammps_workshop_2017')

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
