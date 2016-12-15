folder('build-envs-dsl') {
  description('We use Docker images to set up our various build environments. These projects build the docker images and publish them on DockerHub.')
}

def scripts = ['centos_6', 'centos_7', 'centos_latest',
               'fedora_20', 'fedora_21', 'fedora_22', 'fedora_23', 'fedora_24', 'fedora_latest',
               'opensuse_13.1', 'opensuse_13.2', 'opensuse_42.1',
               'ubuntu_12.04', 'ubuntu_14.04', 'ubuntu_16.04', 'ubuntu_latest']

scripts.each { name ->
    pipelineJob("build-envs-dsl/${name}") {
        triggers {
            githubPush()
        }

        concurrentBuild(false)
        quietPeriod(10)

        definition {
            cpsScm {
                scm {
                    git {
                        remote {
                            github('lammps/lammps-testing')
                            credentials('lammps-jenkins')
                        }

                        branches('pipelines')

                        configure { gitScm ->
                            gitScm / 'extensions' << 'hudson.plugins.git.extensions.impl.PathRestriction' {
                              includedRegions("pipelines/build-envs/${name}.groovy")
                              excludedRegions('.*')
                          }
                        }
                    }
                }
                scriptPath("pipelines/build-envs/${name}.groovy")
            }
        }
    }
}

listView('build-envs-dsl/CentOS') {
  jobs {
    regex("centos_.*")
  }
  columns {
    status()
    weather()
    name()
    lastSuccess()
    lastFailure()
    lastDuration()
    buildButton()
  }
}

listView('build-envs-dsl/Fedora') {
  jobs {
    regex("fedora_.*")
  }
  columns {
    status()
    weather()
    name()
    lastSuccess()
    lastFailure()
    lastDuration()
    buildButton()
  }
}

listView('build-envs-dsl/OpenSUSE') {
  jobs {
    regex("centos_.*")
  }
  columns {
    status()
    weather()
    name()
    lastSuccess()
    lastFailure()
    lastDuration()
    buildButton()
  }
}

listView('build-envs-dsl/Ubuntu') {
  jobs {
    regex("centos_.*")
  }
  columns {
    status()
    weather()
    name()
    lastSuccess()
    lastFailure()
    lastDuration()
    buildButton()
  }
}
