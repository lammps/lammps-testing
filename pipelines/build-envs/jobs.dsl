folder('build-envs') {
  description('We use Docker images to set up our various build environments. These projects build the docker images and publish them on DockerHub.')
}

def scripts = ['fedora_29', 'fedora_29_cross', 'ubuntu_latest', 'ubuntu_18.04_cuda_10.0', 'centos_7']

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
