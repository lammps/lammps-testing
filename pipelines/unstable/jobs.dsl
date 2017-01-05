folder('lammps/unstable')

def scripts = ['serial-gcc', 'serial-clang', 'openmpi-gcc']

scripts.each { name ->
    pipelineJob("lammps/unstable/${name}") {
        triggers {
            githubPush()
        }

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
                              includedRegions("pipelines/unstable/${name}.groovy")
                              excludedRegions('.*')
                          }
                        }
                    }
                }
                scriptPath("pipelines/unstable/${name}.groovy")
            }
        }
    }
}
