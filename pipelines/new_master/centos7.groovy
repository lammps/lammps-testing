echo 'Running builds on CentOS 7'

def scripts = [
    'cmake_mpi_smallbig_shared', 
    'cmake_mpi_openmp_smallbig_shared', 
    'cmake_mpi_bigbig_shared', 
    'cmake_serial_smallsmall_static'
    ]

def container_image = 'lammps_testing:centos_7'

def jobs = scripts.collectEntries {
    ["${it}": {
        build job: "centos7/${it}",
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
