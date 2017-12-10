folder('build-envs') {
  description('We use Docker images to set up our various build environments. These projects build the docker images and publish them on DockerHub.')
}

def scripts = ['centos_6', 'centos_7', 'centos_latest',
               'fedora_21', 'fedora_22', 'fedora_23', 'fedora_24', 'fedora_25', 'fedora_26', 'fedora_27', 'fedora_latest',
               'opensuse_42.1', 'opensuse_42.2', 'opensuse_42.3',
               'ubuntu_12.04', 'ubuntu_14.04', 'ubuntu_16.04', 'ubuntu_latest']

scripts.each { name ->
    pipelineJob("build-envs/${name}") {
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

                        branches('master')

                        configure { gitScm ->
                            gitScm / 'extensions' << 'hudson.plugins.git.extensions.impl.PathRestriction' {
                              includedRegions("pipelines/build-envs/${name}.groovy")
                          }
                        }
                    }
                }
                scriptPath("pipelines/build-envs/${name}.groovy")
            }
        }
    }
}

listView('build-envs/CentOS') {
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

listView('build-envs/Fedora') {
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

listView('build-envs/OpenSUSE') {
  jobs {
    regex("opensuse_.*")
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

listView('build-envs/Ubuntu') {
  jobs {
    regex("ubuntu_.*")
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
