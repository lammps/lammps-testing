import hudson.FilePath
import jenkins.model.Jenkins

def createFilePath(path) {
    if (env['NODE_NAME'] == null) {
        error "envvar NODE_NAME is not set, probably not inside an node {} or running an older version of Jenkins!";
    } else if (env['NODE_NAME'].equals("master")) {
        return new FilePath(path);
    } else {
        return new FilePath(Jenkins.getInstance().getComputer(env['NODE_NAME']).getChannel(), path);
    }
}

node('atlas2') {
    echo 'Running builds on Ubuntu'

    def workspace_parent = createFilePath(params.WORKSPACE_PARENT)
    def testing_dir = workspace_parent.child('lammps-testing')
    def scripts_dir = testing_dir.child('scripts/simple')
    def container_scripts = scripts_dir.child('ubuntu').list()

    container_scripts.each { container ->
        echo "Building ${container}!"
    }

    def scripts = [
        'cmake_mpi_smallbig_shared', 
        'cmake_mpi_openmp_smallbig_shared', 
        'cmake_mpi_bigbig_shared', 
        'cmake_serial_smallsmall_static'
        ]

    def container_image = 'lammps_testing:ubuntu_latest'

    def jobs = scripts.collectEntries {
        ["${it}": {
            build job: "ubuntu/${it}",
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
}
