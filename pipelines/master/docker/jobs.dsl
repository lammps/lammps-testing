folder('lammps/master/docker')

def scripts = ['ubuntu18.04_openmpi_py2', 'ubuntu18.04_openmpi_py3', 'centos7_openmpi_py2', 'centos7_openmpi_py3']

scripts.each { name ->
    pipelineJob("lammps/master/docker/${name}") {
        triggers {
            githubPush()
        }

        concurrentBuild(false)

        definition {
            cps {
                script(readFileFromWorkspace("pipelines/master/docker/${name}.groovy"))
                sandbox()
            }
        }
    }
}
