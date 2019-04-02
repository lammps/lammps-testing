folder('lammps/master')

def scripts = ['serial', 'shlib', 'openmpi', 'serial-clang', 'shlib-clang', 'openmpi-clang', 'build-docs', 'testing', 'testing-omp', 'regression', 'intel', 'kokkos-omp']

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

def cmake_scripts = ['cmake-serial', 'cmake-testing', 'cmake-testing-omp', 'cmake-win32-serial', 'cmake-win64-serial']

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
