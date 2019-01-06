folder('lammps/master')

def scripts = ['new-serial', 'new-shlib', 'new-openmpi', 'new-serial-clang', 'new-shlib-clang', 'new-openmpi-clang', 'new-build-docs', 'new-testing', 'new-testing-omp', 'new-regression', 'new-intel']

scripts.each { name ->
    pipelineJob("lammps/master/${name}") {
        triggers {
            githubPush()
        }

        concurrentBuild(false)

        definition {
            cps {
                script(readFileFromWorkspace('pipelines/master/master.groovy'))
                sandbox()
            }
        }
    }
}
