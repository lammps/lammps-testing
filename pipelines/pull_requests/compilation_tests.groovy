@Library(value='lammps_testing', changelog=false)
import org.lammps.ci.Utils

def project_url = 'https://github.com/lammps/lammps.git'
def set_github_status = true
def send_slack = true

def lammps_testing_branch = 'master'
def workspace = '/mnt/lammps/workspace/' + env.JOB_NAME

node('atlas2') {
    ws(workspace) {
    def utils = new Utils()


    stage('Checkout') {
        dir('lammps') {
            branch_name = "origin-pull/pull/${env.GITHUB_PR_NUMBER}/merge"
            refspec = "+refs/pull/${env.GITHUB_PR_NUMBER}/merge:refs/remotes/origin-pull/pull/${env.GITHUB_PR_NUMBER}/merge"
            checkout changelog: true, poll: true, scm: [$class: 'GitSCM', branches: [[name: branch_name]], doGenerateSubmoduleConfigurations: false, extensions: [[$class: 'CleanCheckout'], [$class: 'CloneOption', depth: 1, noTags: false, reference: '', shallow: true]], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'lammps-jenkins', name: 'origin-pull', refspec: refspec, url: project_url]]]
        }

        dir('lammps-testing') {
            checkout changelog: false, poll: false, scm: [$class: 'GitSCM', branches: [[name: "*/${lammps_testing_branch}"]], doGenerateSubmoduleConfigurations: false, extensions: [], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'lammps-jenkins', url: 'https://github.com/lammps/lammps-testing']]]
        }
    }

    if (set_github_status) {
        utils.setGitHubCommitStatus(project_url, env.JOB_NAME, env.GITHUB_PR_HEAD_SHA, 'building...', 'PENDING')
    }

    def yaml_files = findFiles glob: 'lammps-testing/scripts/*.yml'


    def configurations = yaml_files.collectEntries { yaml_file -> get_configuration(yaml_file)  }

    def jobs = [:]
    def err = null
    def ccache_dir = ".ccache"

    try {
        stage('Compilation') {
            configurations.each { container, config ->
                jobs["${container}"] = launch_build("${container}/compilation_tests", env.GITHUB_PR_HEAD_SHA, env.WORKSPACE, ccache_dir)
            }
            parallel jobs
        }
    } catch (caughtErr) {
        err = caughtErr
        currentBuild.result = 'FAILURE'
    } finally {
        if (currentBuild.result == 'FAILURE') {
            if (set_github_status) {
                utils.setGitHubCommitStatus(project_url, env.JOB_NAME, env.GITHUB_PR_HEAD_SHA, 'build failed!', 'FAILURE')
            }
            if (send_slack) {
                slackSend color: 'bad', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} failed!"
            }
        } else {
            if (set_github_status) {
                utils.setGitHubCommitStatus(project_url, env.JOB_NAME, env.GITHUB_PR_HEAD_SHA, 'build successful!', 'SUCCESS')
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
    return ["${name}": [
        "display_name": config.display_name.toString(),
        "builds": config.builds.collect({ it.toString() })
    ]]
}

def launch_build(job_name, commit, workspace, ccache_dir) {
    return {
        build job: job_name, parameters: [ string(name: 'GIT_COMMIT', value: commit), string(name: 'WORKSPACE_PARENT', value: workspace), string(name: 'CCACHE_DIR', value: ccache_dir) ]
    }
}
