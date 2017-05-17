folder('lammps/pull-requests')

job('lammps/pull-requests/regression-pr') {
    scm {
        git {
            branch('origin-pull/pull/${GITHUB_PR_NUMBER}/merge')
            remote {
                credentials('lammps-jenkins')
                github('lammps/lammps')
                name('origin-pull')
                refspec('+refs/pull/${GITHUB_PR_NUMBER}/merge:refs/remotes/origin-pull/pull/${GITHUB_PR_NUMBER}/merge')
            }
            extensions {
                cleanAfterCheckout()
            }
        }
    }

    triggers {
        gitHubPRTrigger {
            spec("* * * * *")
            triggerMode('HEAVY_HOOKS')
            events {
                gitHubPRLabelAddedEvent {
                    label {
                        labels('full-regression-test')
                    }
                }
            }
        }
    }

    wrappers {
        buildInDocker {
            image('rbberger/lammps-testing:ubuntu_latest')
        }
        colorizeOutput()
        timeout {
            failBuild()
            absolute(120)
        }
    }

    steps {
        shell(readFileFromWorkspace('pipelines/pull-requests/regression-pr.sh'))
    }
}
