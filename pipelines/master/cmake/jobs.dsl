folder('lammps/master/cmake')

def scripts = ['serial', 'openmpi', 'enable_all']

def default_packages = [
'ASPHERE', 'BODY', 'CLASS2', 'COLLOID', 'COMPRESS', 'CORESHELL', 'DIPOLE',
'GRANULAR', 'KSPACE', 'MANYBODY', 'MC', 'MEAM', 'MISC', 'MOLECULE', 'PERI',
'QEQ', 'REAX', 'REPLICA', 'RIGID', 'SHOCK', 'SNAP', 'SRD'
]

def other_packages = [
'KIM', 'PYTHON', 'MSCG', 'MPIIO', 'VORONOI', 'POEMS', 'LATTE', 'USER-ATC',
'USER-AWPMD', 'USER-CGDNA', 'USER-MESO', 'USER-CGSDK', 'USER-COLVARS',
'USER-DIFFRACTION', 'USER-DPD', 'USER-DRUDE', 'USER-EFF', 'USER-FEP',
'USER-H5MD', 'USER-LB', 'USER-MANIFOLD', 'USER-MEAMC', 'USER-MGPT',
'USER-MISC', 'USER-MOLFILE', 'USER-NETCDF', 'USER-PHONON', 'USER-QTB',
'USER-REAXC', 'USER-SMD', 'USER-SMTBQ', 'USER-SPH', 'USER-TALLY', 'USER-UEF',
'USER-VTK', 'USER-QUIP', 'USER-QMMM'
]

def packages = default_packages + other_packages


scripts.each { name ->
    pipelineJob("lammps/master/cmake/${name}") {
        triggers {
            githubPush()
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

                        branches('master')

                        configure { gitScm ->
                            gitScm / 'extensions' << 'hudson.plugins.git.extensions.impl.PathRestriction' {
                              includedRegions("pipelines/master/cmake/${name}.groovy")
                          }
                        }
                    }
                }
                scriptPath("pipelines/master/cmake/${name}.groovy")
            }
        }
    }
}

folder('lammps/master/cmake/packages')

packages.each { name ->
    pipelineJob("lammps/master/cmake/packages/${name}") {
        environmentVariables {
            env("PACKAGE", name)
            env("PACKAGE_TEST_DIRS", name.toLowerCase())
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

                        branches('master')

                        configure { gitScm ->
                            gitScm / 'extensions' << 'hudson.plugins.git.extensions.impl.PathRestriction' {
                              includedRegions("pipelines/master/cmake/build_package.groovy")
                          }
                        }
                    }
                }
                scriptPath("pipelines/master/cmake/build_package.groovy")
            }
        }
    }
}
