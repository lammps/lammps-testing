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
        gitHubPushTrigger()
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
        gitHubPRStatusBuilder {
            statusMessage {
                content('${GITHUB_PR_COND_REF} run started')
            }
        }
        shell(readFileFromWorkspace('pipelines/pull-requests/regression-pr.sh'))
    }

    publishers {
        warnings(['GNU Make + GNU C Compiler (gcc)'], [:]) {
            resolveRelativePaths()
        }
        junit {
            testResults('lammps-testing/nosetests-*.xml')
        }
        analysisCollector {
            warnings()
        }
        gitHubPRBuildStatusPublisher {
            statusMsg {
                content('${GITHUB_PR_COND_REF} run ended')
            }
            unstableAs('FAILURE')
            buildMessage {
                successMsg {
                  content('${GITHUB_PR_COND_REF} build successful!')
                }
                failureMsg {
                  content('${GITHUB_PR_COND_REF} build failed!')
                }
            }
            statusVerifier {
            }
            errorHandler {
            }
        }
        slackNotifier {
            includeTestSummary(true)
            notifyAborted(true)
            notifyBackToNormal(true)
            notifyFailure(true)
            notifyNotBuilt(true)
            notifyRegression(true)
            notifyRepeatedFailure(true)
            notifySuccess(true)
            notifyUnstable(true)
            startNotification(false)
        }
    }
}
