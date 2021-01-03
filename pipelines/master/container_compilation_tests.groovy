import hudson.FilePath;

node('multicore') {
    env.LAMMPS_DIR = "${params.WORKSPACE_PARENT}/lammps"
    env.LAMMPS_TESTING_DIR = "${params.WORKSPACE_PARENT}/lammps-testing"

    def yaml_path = env.LAMMPS_TESTING_DIR + "/scripts/${params.CONTAINER}.yml"
    def config = get_configuration(yaml_path)

    def err = null

    try {
        def jobs = config.builds.collectEntries { build ->
            ["${build}": launch_build("${container}/${build}", params.GIT_COMMIT, params.WORKSPACE_PARENT)]
        }

        stage(config.display_name) {
            echo "Running ${config.display_name}"
            parallel jobs
        }
    } catch (caughtErr) {
        err = caughtErr
        currentBuild.result = 'FAILURE'
    } finally {
        if (currentBuild.result == 'FAILURE') {
            if (send_slack) {
                slackSend color: 'bad', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} failed!"
            }
        } else {
            if (send_slack) {
                slackSend color: 'good', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} succeeded!"
            }
        }

        if(err) {
            throw err
        }
    }
}

def get_configuration(yaml_file) {
    def fp = new FilePath(yaml_file)
    def name = fp.getBaseName()
    def config  = readYaml(file: yaml_file)
    return ["${name}": [
        "display_name": config.display_name.toString(),
        "builds": config.builds.collect({ it.toString() })
    ]]
}

def launch_build(job_name, commit, workspace) {
    return {
        build job: job_name, parameters: [ string(name: 'GIT_COMMIT', value: commit), string(name: 'WORKSPACE_PARENT', value: workspace) ]
    }
}
