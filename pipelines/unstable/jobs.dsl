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

                        extensions {
                            pathRestriction {
                                includedRegions("pipelines/unstable/${name}.groovy")
                            }
                        }
                    }
                }
                scriptPath("pipelines/unstable/${name}.groovy")
            }
        }
    }

}
