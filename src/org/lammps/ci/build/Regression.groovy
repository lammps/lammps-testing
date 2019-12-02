package org.lammps.ci.build

class Regression extends LegacyTesting {
    Regression(steps) {
        super('jenkins/regression', steps)
        build.lammps_mach = 'mpi'
        build.lammps_target = 'mpi'
        build.lammps_size = LAMMPS_SIZES.SMALLBIG
        build.compiler = 'mpicxx'

        build.packages << 'yes-asphere'
        build.packages << 'yes-body'
        build.packages << 'yes-class2'
        build.packages << 'yes-colloid'
        build.packages << 'yes-compress'
        build.packages << 'yes-coreshell'
        build.packages << 'yes-dipole'
        build.packages << 'yes-granular'
        build.packages << 'yes-kspace'
        build.packages << 'yes-manybody'
        build.packages << 'yes-mc'
        build.packages << 'yes-misc'
        build.packages << 'yes-molecule'
        build.packages << 'yes-mpiio'
        build.packages << 'yes-opt'
        build.packages << 'yes-peri'
        build.packages << 'yes-poems'
        build.packages << 'yes-python'
        build.packages << 'yes-qeq'
        build.packages << 'yes-replica'
        build.packages << 'yes-rigid'
        build.packages << 'yes-shock'
        build.packages << 'yes-snap'
        build.packages << 'yes-spin'
        build.packages << 'yes-srd'
        build.packages << 'yes-voronoi'
        build.packages << 'yes-user-atc'
        build.packages << 'yes-user-awpmd'
        build.packages << 'yes-user-bocs'
        build.packages << 'yes-user-cgdna'
        build.packages << 'yes-user-cgsdk'
        build.packages << 'yes-user-colvars'
        build.packages << 'yes-user-diffraction'
        build.packages << 'yes-user-dpd'
        build.packages << 'yes-user-drude'
        build.packages << 'yes-user-eff'
        build.packages << 'yes-user-fep'
        build.packages << 'yes-user-lb'
        build.packages << 'yes-user-manyfold'
        build.packages << 'yes-user-meamc'
        build.packages << 'yes-user-meso'
        build.packages << 'yes-user-misc'
        build.packages << 'yes-user-mofff'
        build.packages << 'yes-user-molfile'
        build.packages << 'yes-user-phonon'
        build.packages << 'yes-user-qmmm'
        build.packages << 'yes-user-qtb'
        build.packages << 'yes-user-reaxc'
        build.packages << 'yes-user-smd'
        build.packages << 'yes-user-smtbq'
        build.packages << 'yes-user-sph'
        build.packages << 'yes-user-tally'
        build.packages << 'yes-user-uef'
        build.packages << 'yes-user-yaff'

        test_modes.serial = true
    }

    def test() {
        steps.sh 'rm -rf lammps-testing/tests/examples/USER/eff'
        steps.sh 'rm -rf lammps-testing/tests/examples/USER/misc/imd'
        steps.sh 'rm -rf lammps-testing/tests/examples/USER/fep'
        steps.sh 'rm -rf lammps-testing/tests/examples/USER/lb'
        steps.sh 'rm -rf lammps-testing/tests/examples/HEAT'
        steps.sh 'rm -rf lammps-testing/tests/examples/COUPLE'

        // run regression tests
        steps.sh '''#!/bin/bash -l
        source pyenv/bin/activate
        rm *.out *.xml || true
        python lammps-testing/lammps_testing/regression.py 8 "mpiexec -np 8 ${LAMMPS_BINARY} -v CORES 8" lammps-testing/tests/examples -exclude kim gcmc mscg nemd prd tad neb VISCOSITY ASPHERE USER/mgpt USER/dpd/dpdrx-shardlow balance accelerate USER/atc USER/quip USER/misc/grem USER/misc/i-pi USER/misc/pimd USER/cg-cmm 2>&1 |tee test0.out
        python lammps-testing/lammps_testing/regression.py 8 "mpiexec -np 8 ${LAMMPS_BINARY} -partition 4x2 -v CORES 8" lammps-testing/tests/examples -only prd 2>&1 |tee test1.out
        deactivate
        '''

        // generate regression XML
        steps.sh 'python lammps-testing/lammps_testing/generate_regression_xml.py --test-dir $PWD/lammps-testing/tests/ --log-file test0.out --out-file regression_00.xml'
        steps.sh 'python lammps-testing/lammps_testing/generate_regression_xml.py --test-dir $PWD/lammps-testing/tests/ --log-file test1.out --out-file regression_01.xml'
    }

    def collect_reports() {
        steps.junit 'regression_*.xml'
    }
}
