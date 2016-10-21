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
                    }
                }
                scriptPath("pipelines/unstable/${name}.groovy")
            }
        }
    }

}
