echo 'Running ${params.CONTAINER_DISPLAY_NAME}'

def scripts = params.CONTAINER_BUILDS.split(',')

def jobs = scripts.collectEntries {
    ["${it}": {
        build job: "${params.CONTAINER_NAME}/${it}",
            parameters: [
                string(name: 'GIT_COMMIT', value: params.GIT_COMMIT),
                string(name: 'WORKSPACE_PARENT', value: params.WORKSPACE_PARENT),
                ]
    }]
}

stage('Build'){
    parallel jobs
}
