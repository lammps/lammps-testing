package org.lammps.ci

def setGitHubCommitStatus(project_url, build_name, git_commit, message, state) {
    if (env.LAMMPS_REPORT_GH_STATUS.toBoolean()) {
        step([$class: 'GitHubCommitStatusSetter', commitShaSource: [$class: 'ManuallyEnteredShaSource', sha: git_commit], contextSource: [$class: 'ManuallyEnteredCommitContextSource', context: build_name], reposSource: [$class: 'ManuallyEnteredRepositorySource', url: project_url], statusResultSource: [$class: 'ConditionalStatusResultSource', results: [[$class: 'AnyBuildResult', message: message, state: state]]]])
    }
}

return this
