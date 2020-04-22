echo 'Running Windows cross compilation builds on Fedora'

def scripts = [
    'cmake_serial_smallsmall_static_win32',
    'cmake_mpi_openmp_smallbig_shared_win64', 
    ]

def container_image = 'lammps_testing:fedora_29_cross'

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
