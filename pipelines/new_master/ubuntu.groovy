echo 'Running builds on Ubuntu'

def scripts = [
    'cmake_mpi_smallbig_shared', 
    'cmake_mpi_openmp_smallbig_shared', 
    'cmake_mpi_bigbig_shared', 
    'cmake_serial_smallsmall_static'
    ]

def container_image = 'lammps_testing:ubuntu_latest'

def jobs = scripts.collectEntries {
    ["${it}": {
        build job: "${it}",
            parameters: [
                string(name: 'GIT_COMMIT', value: params.GIT_COMMIT), 
                string(name: 'WORKSPACE_PARENT', value: params.WORKSPACE_PARENT), 
                string(name: 'CONTAINER_IMAGE', value: container_image)
                ]
    }]
}

stage('Build'){
    parallel jobs
}
