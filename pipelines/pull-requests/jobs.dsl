folder('lammps-git-training/pull-requests')

def scripts = ['build-docs-pr']

scripts.each { name ->
    pipelineJob("lammps-git-training/pull-requests/${name}") {
        triggers {
            gitHubPRTrigger {
                spec("")
                triggerMode('HEAVY_HOOKS')
                events {
                    gitHubPROpenEvent()
                    gitHubPRCommitEvent()
                }
            }
        }

        concurrentBuild(false)
        quietPeriod(300)

        definition {
            cpsScm {
                scm {
                    git {
                        remote {
                            github('lammps/lammps-testing')
                            credentials('lammps-jenkins')
                        }

                        branches('lammps_workshop_2017')

                        configure { gitScm ->
                            gitScm / 'extensions' << 'hudson.plugins.git.extensions.impl.PathRestriction' {
                              includedRegions("pipelines/pull-requests/${name}.groovy")
                          }
                        }
                    }
                }
                scriptPath("pipelines/pull-requests/${name}.groovy")
            }
        }

        properties {
            githubProjectUrl("https://github.com/lammps/lammps-git-tutorial")
        }
    }
}
