@Library(value='lammps_testing', changelog=false)
import org.lammps.ci.Utils

def project_url = 'https://github.com/lammps/lammps.git'
def set_github_status = true
def send_slack = true

def lammps_branch = "develop"
def lammps_testing_branch = "master"
def potentials = '/mnt/lammps/downloads/potentials'
def workspace = '/mnt/lammps/workspace/' + env.JOB_NAME

node('atlas2') {
    ws(workspace) {
    def utils = new Utils()


    stage('Checkout') {
        dir('lammps') {
            commit = checkout([$class: 'GitSCM', branches: [[name: "*/${lammps_branch}"]], doGenerateSubmoduleConfigurations: false, extensions: [[$class: 'CloneOption', depth: 1, noTags: false, reference: '', shallow: true]], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'lammps-jenkins', url: 'https://github.com/lammps/lammps']]])
            sh "cp -f ${potentials}/* potentials/"
        }

        dir('lammps-testing') {
            checkout changelog: false, poll: false, scm: [$class: 'GitSCM', branches: [[name: "*/${lammps_testing_branch}"]], doGenerateSubmoduleConfigurations: false, extensions: [], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'lammps-jenkins', url: 'https://github.com/lammps/lammps-testing']]]
        }
    }

    if (set_github_status) {
        utils.setGitHubCommitStatus(project_url, env.JOB_NAME, commit.GIT_COMMIT, 'building...', 'PENDING')
    }

    def yaml_files = findFiles glob: 'lammps-testing/scripts/*.yml'

    def configurations = yaml_files.collectEntries { yaml_file -> get_configuration(yaml_file)  }

    def jobs = [:]
    def err = null

    try {
        stage('Compilation') {
            configurations.each { container, config ->
                if(config.builds.size() > 0) {
                    jobs["${container}"] = launch_build("${container}/compilation_tests", commit.GIT_COMMIT, env.WORKSPACE)
                }
            }
            parallel jobs
        }
    } catch (caughtErr) {
        err = caughtErr
        currentBuild.result = 'FAILURE'
    } finally {
        if (currentBuild.result == 'FAILURE') {
            if (set_github_status) {
                utils.setGitHubCommitStatus(project_url, env.JOB_NAME, commit.GIT_COMMIT, 'build failed!', 'FAILURE')
            }
            if (send_slack) {
                slackSend color: 'bad', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} failed!"
            }
        } else {
            if (set_github_status) {
                utils.setGitHubCommitStatus(project_url, env.JOB_NAME, commit.GIT_COMMIT, 'build successful!', 'SUCCESS')
            }
            if (send_slack) {
                slackSend color: 'good', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} succeeded!"
            }
        }

        if(err) {
            throw err
        }
    }
    }
}

def get_configuration(yaml_file) {
    def name = yaml_file.name.take(yaml_file.name.lastIndexOf('.'))
    def config  = readYaml(file: yaml_file.path)

    def display_name = name
    def builds = []
    def run_tests  = []
    def regression_tests = []
    def unit_tests = []

    if(config.containsKey('display_name')) {
        display_name = config.display_name.toString()
    }

    if(config.containsKey('builds')) {
        builds = config.builds.collect({ it.toString() })
    }

    if(config.containsKey('run_tests')) {
        run_tests = config.run_tests.collect({ it.toString() })
    }

    if(config.containsKey('regression_tests')) {
        regression_tests = config.regression_tests.collect({ it.toString() })
    }

    if(config.containsKey('unit_tests')) {
        unit_tests = config.unit_tests.collect({ it.toString() })
    }

    return ["${name}": [
        "display_name": display_name,
        "builds": builds,
        "run_tests": run_tests,
        "regression_tests": regression_tests,
        "unit_tests": unit_tests,
    ]]
}

def launch_build(job_name, commit, workspace) {
    return {
        build job: job_name, parameters: [ string(name: 'GIT_COMMIT', value: commit), string(name: 'WORKSPACE_PARENT', value: workspace) ]
    }
}
