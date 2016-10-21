folder('dsl')

def scripts = ['serial-gcc', 'serial-clang']

scripts.each { name ->
    pipelineJob("dsl/${name}") {
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

                        branches('pipelines')

                        configure { gitScm ->
                            gitScm / 'extensions' << 'hudson.plugins.git.extensions.impl.PathRestriction' {
                              includedRegions("pipelines/unstable/${name}.groovy")
                              excludedRegions('')
                          }
                        }
                    }
                }
                scriptPath("pipelines/unstable/${name}.groovy")
            }
        }
    }
}
