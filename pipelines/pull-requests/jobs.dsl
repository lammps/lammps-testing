folder('lammps/pull-requests')

def scripts = ['regression-pr']

scripts.each { script_name ->
    pipelineJob("lammps/pull-requests/${script_name}") {
        triggers {
            onPullRequest {
                mode {
                    heavyHooks()
                }
                events {
                    labelAdded('test-for-regression')
                }
            }
        }

        definition {
            cpsScm {
                scm {
                    git {
                        remote {
                            name('lammps-testing')
                            github('lammps/lammps-testing')
                            credentials('lammps-jenkins')
                        }

                        remote {
                            name('lammps')
                            github('lammps/lammps')
                            credentials('lammps-jenkins')
                        }

                        branches('lammps-testing/master')
                    }
                }
                scriptPath("pipelines/pull-requests/${script_name}.groovy")
            }
        }
    }
}
