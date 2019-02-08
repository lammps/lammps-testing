folder('lammps/master')

def scripts = ['new-serial', 'new-shlib', 'new-openmpi', 'new-serial-clang', 'new-shlib-clang', 'new-openmpi-clang', 'new-build-docs', 'new-testing', 'new-testing-omp', 'new-regression', 'new-intel', 'new-kokkos-omp']

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

folder('lammps/master/cmake')

def cmake_scripts = ['new-cmake-serial', 'new-cmake-testing', 'new-cmake-testing-omp']

cmake_scripts.each { name ->
    pipelineJob("lammps/master/cmake/${name}") {
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
